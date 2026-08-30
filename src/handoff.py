"""Handoff workflow: triage → FAQ agent or human consultant."""

from __future__ import annotations

import asyncio
import sys
from uuid import uuid4

from agno.agent import Agent
from agno.db.base import BaseDb
from agno.db.in_memory import InMemoryDb
from agno.workflow import Router, Step, Workflow
from agno.workflow.types import StepInput, StepOutput
from agno.db.sqlite import SqliteDb

from agents.faq.agent import create_faq_agent
from agents.faq.knowledge_base import FAQ
from agents.triage.agent import Triage, create_triage_agent
from config import Settings
from notifications.notifier import HandoffNotifier

TRIAGE_STEP = "triage"


def _triage_of(step_input: StepInput) -> Triage:
    """The triage decision, looked up by step name.

    `get_step_output` searches nested steps too, so this works both right
    after the triage step and inside the Router's chosen step.
    """
    output = step_input.get_step_output(TRIAGE_STEP)
    if output is None:
        raise RuntimeError(f"Step '{TRIAGE_STEP}' produced no output")
    if not isinstance(output.content, Triage):
        # Agent errors are surfaced as a plain string in the step content.
        raise RuntimeError(
            f"Step '{TRIAGE_STEP}' did not return a Triage decision: {output.content!r}"
        )
    return output.content


def _question(step_input: StepInput) -> StepOutput:
    """Returns the user's question as a StepOutput."""
    return StepOutput(content=step_input.get_input_as_string())


def _make_human_handoff(notifier: HandoffNotifier):
    """Builds the human-handoff step executor.
    """

    def _human_handoff(step_input: StepInput) -> StepOutput:
        """Notifies a human consultant and returns the canned reply."""
        triage = _triage_of(step_input)
        message = f"User's question requires human intervention: {triage.reason}"
        notifier.notify(message)

        return StepOutput(
            content=(
                f"To pytanie wymaga kontaktu z konsultantem ({triage.reason}).\n\n"
                f"{FAQ['helpline contact']}"
            )
        )

    return _human_handoff


def create_handoff_workflow(
    settings: Settings,
    db: BaseDb,
    triage_agent: Agent | None = None,
    faq_agent: Agent | None = None,
    num_history_runs: int = 5,
    notifier: HandoffNotifier | None = None,
) -> Workflow:
    """Builds the handoff workflow.

    """
    triage_agent = triage_agent or create_triage_agent(settings, db=db)
    faq_agent = faq_agent or create_faq_agent(settings, db=db)
    faq_agent.add_history_to_context = False
    notifier = notifier or HandoffNotifier.from_settings(settings)

    triage_step = Step(name=TRIAGE_STEP, agent=triage_agent)
    question_step = Step(name="Question Step", executor=_question)
    faq_step = Step(name="FAQ Step", agent=faq_agent)
    human_step = Step(name="Human Handoff Step", executor=_make_human_handoff(notifier))

    def route(step_input: StepInput) -> list[Step]:
        if _triage_of(step_input).target == "human":
            return [human_step]
        return [question_step, faq_step]

    router = Router(name="route", choices=[human_step, question_step, faq_step], selector=route)

    return Workflow(
        name="Handoff Workflow",
        steps=[triage_step, router],
        db=db,
        add_workflow_history_to_steps=True,
        num_history_runs=num_history_runs,
    )


async def aask(question: str, workflow: Workflow, session_id: str):
    """Runs one turn of the conversation identified by `session_id`."""
    return await workflow.arun(input=question, session_id=session_id)


def main() -> None:
    settings = Settings()
    if settings.model_provider == "openai" and not settings.openai_api_key:
        sys.exit(
            "Missing API key. Set OPENAI_API_KEY in the .env file in the working directory\n"
            "(or set the OPENAI_API_KEY environment variable)."
        )
    db = SqliteDb(db_file="faq_agent_os.db")

    workflow = create_handoff_workflow(settings, db=db)
    session_id = str(uuid4())

    asyncio.run(_amain(workflow, session_id))


async def _amain(workflow: Workflow, session_id: str) -> None:
    if len(sys.argv) > 1:
        result = await aask(" ".join(sys.argv[1:]), workflow, session_id)
        print(result.content)
        return

    print("Example Air handoff workflow (type 'exit' to quit)")
    while True:
        try:
            question = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not question:
            continue
        if question.lower() in {"exit", "quit"}:
            break
        result = await aask(question, workflow, session_id)
        print(f"\nAgent: {result.content}")


if __name__ == "__main__":
    main()
