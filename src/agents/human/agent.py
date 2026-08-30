"""Human hand-off agent definition.

The "human" member of the support Team (`support_team.py`). It answers no
question itself: it notifies a consultant (`notify_consultant` tool) and
repeats the canned reply to the passenger. In the Workflow variant
(`handoff.py`) this is a plain function; a Team needs an agent here.
"""

from __future__ import annotations

from agno.agent import Agent
from agno.db.base import BaseDb
from agno.models.openai import OpenAIChat

from agents.human.tools import HandoffTools
from config import Settings, create_model
from notifications import HandoffNotifier

ROLE = "Przejmuje sprawy dotyczące konkretnej rezerwacji, lotu lub reklamacji pasażera"

INSTRUCTIONS = (
    "Jesteś agentem przekazującym sprawy pasażerów linii Example Air do konsultanta. "
    "Nie odpowiadasz merytorycznie i nie masz dostępu do rezerwacji.\n"
    "- Zawsze wywołaj narzędzie notify_consultant: w `question` podaj wiadomość pasażera "
    "słowo w słowo, w `reason` krótki powód (np. 'status konkretnego lotu').\n"
    "- Odpowiedz pasażerowi DOKŁADNIE tekstem zwróconym przez narzędzie — "
    "bez zmian, skrótów ani dopisków."
)


def create_human_agent(
    settings: Settings,
    notifier: HandoffNotifier | None = None,
    db: BaseDb | None = None,
) -> Agent:
    """Builds the human hand-off agent bound to `notifier` (console by default)."""
    return Agent(
        name="Human Agent",
        role=ROLE,
        model=create_model(settings),
        instructions=INSTRUCTIONS,
        tools=[HandoffTools(notifier)],
        db=db,
    )
