import sys

from agno.agent import Agent
from agno.db.base import BaseDb
from agno.models.base import Model
from agno.models.openai import OpenAIChat
from config import create_model
from agno.team import Team, TeamMode

from agents.faq.agent import create_faq_agent
from agents.human.agent import create_human_agent
from config import Settings
from notifications import HandoffNotifier

TEAM_INSTRUCTIONS = (
    "Jesteś recepcją obsługi klienta linii lotniczej Example Air.\n"
    "- Sprawy dotyczące konkretnej rezerwacji, lotu, biletu lub reklamacji pasażera "
    "kieruj do Human Agent.\n"
    "- Wszystkie pozostałe pytania (zasady, opłaty, procedury) kieruj do FAQ Agent."
)


def create_support_team(
    settings: Settings,
    db: BaseDb | None = None,
    faq_agent: Agent | None = None,
    human_agent: Agent | None = None,
    notifier: HandoffNotifier | None = None,
    leader_model: Model | None = None,
) -> Team:
    """Builds the leader -> (FAQ Agent | Human Agent) team.
    """
    faq_agent = faq_agent or create_faq_agent(settings, db=db)
    if human_agent is None:
        notifier = notifier or HandoffNotifier.from_settings(settings)
        human_agent = create_human_agent(settings, notifier=notifier, db=db)
    leader_model = leader_model or create_model(settings)

    return Team(
        name="Support Team",
        mode=TeamMode.route,
        model=leader_model,
        members=[faq_agent, human_agent],
        instructions=TEAM_INSTRUCTIONS,
        determine_input_for_members=False,
        db=db,
    )



def ask(question: str, settings: Settings | None = None) -> str:
    """Runs the support team and returns the chosen member's answer."""
    settings = settings or Settings()
    team = create_support_team(settings)
    return team.run(question).content


async def aask(question: str, settings: Settings | None = None) -> str:
    """Async variant of `ask`."""
    settings = settings or Settings()
    team = create_support_team(settings)
    result = await team.arun(question)
    return result.content


def main() -> None:
    settings = Settings()
    if not settings.openai_api_key:
        sys.exit("Missing API key. Set OPENAI_API_KEY in the .env file.")
    question = " ".join(sys.argv[1:]) or "Ile kosztuje nadbagaż?"
    print(ask(question, settings=settings))


if __name__ == "__main__":
    main()
