"""FAQ agent definition."""

from __future__ import annotations

from agno.agent import Agent
from agno.db.base import BaseDb
from agno.db.in_memory import InMemoryDb
from agno.models.openai import OpenAIChat

from config import Settings
from agents.faq.tools import FaqTools

INSTRUCTIONS = (
    "Jesteś asystentem obsługi klienta linii lotniczej Example Air. "
    "Odpowiadasz po polsku, krótko i uprzejmie.\n"
    "Zasady:\n"
    "- Zanim odpowiesz na pytanie o zasady przewozu, opłaty czy procedury, "
    "zawsze sprawdź bazę FAQ narzędziem search_faq.\n"
    "- Baza FAQ jest po angielsku — szukaj angielskich słów kluczowych, "
    "a pasażerowi odpowiadaj po polsku.\n"
    "- Odpowiadaj wyłącznie na podstawie informacji z FAQ. Nie wymyślaj "
    "cen, limitów ani procedur, których tam nie ma.\n"
    "- Jeśli FAQ nie zawiera odpowiedzi, powiedz to wprost i skieruj "
    "pasażera na infolinię (temat 'helpline contact').\n"
    "- Nie masz dostępu do rezerwacji pasażerów — sprawy indywidualne "
    "(np. status konkretnego lotu) kieruj na infolinię."
)


def create_agent(settings: Settings, db: BaseDb | None = None) -> Agent:
    """Builds the FAQ agent with the configured model and tools.

    Defaults to an in-memory, per-process session store; pass `db`
    (e.g. a SqliteDb) for a persistent one, as os_app.py does.
    """
    return Agent(
        name="FAQ Agent",
        model=OpenAIChat(id=settings.model_name, api_key=settings.openai_api_key),
        instructions=INSTRUCTIONS,
        tools=[FaqTools()],
        db=db or InMemoryDb(),
        add_history_to_context=True,
    )
