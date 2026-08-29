
from __future__ import annotations

import sys
from uuid import uuid4

from agents.faq.agent import create_faq_agent
from config import Settings


def main() -> None:
    settings = Settings()
    if not settings.openai_api_key:
        sys.exit(
            "Missing API key. Set OPENAI_API_KEY in the .env file in the working directory\n"
            "(or set the OPENAI_API_KEY environment variable)."
        )

    agent = create_faq_agent(settings)

    if len(sys.argv) > 1:
        # One-shot mode: question passed as an argument.
        result = agent.run(" ".join(sys.argv[1:]))
        print(result.content)
        return

    print("Example Air airline FAQ agent (type 'exit' to quit)")
    session_id = str(uuid4())  # ties every turn to the same conversation in the db
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
        result = agent.run(question, session_id=session_id)
        print(f"\nAgent: {result.content}")
