"""Triage agent definition."""

from __future__ import annotations

from typing import Literal

from agno.agent import Agent
from agno.db.base import BaseDb
from pydantic import BaseModel

from config import Settings, create_model

TRIAGE_INSTRUCTIONS = (
    "Jesteś agentem triażu obsługi klienta linii lotniczej Example Air.\n"
    "Zdecyduj, dokąd skierować pytanie pasażera:\n"
    "- target='faq' — pytania ogólne o zasady, opłaty i procedury "
    "(bagaż, odprawa, zmiany rezerwacji, zwroty, zwierzęta, dzieci itp.).\n"
    "- target='human' — sprawy wymagające dostępu do danych konkretnego "
    "pasażera lub rezerwacji (np. status konkretnego lotu, reklamacja "
    "dotycząca już zakupionego biletu)."
)


class Triage(BaseModel):
    """Routing decision made by the triage agent."""

    target: Literal["faq", "human"]
    reason: str


def create_triage_agent(settings: Settings, db: BaseDb | None = None) -> Agent:
    """Builds the triage agent that decides where to hand off the question."""
    return Agent(
        name="Triage Agent",
        model=create_model(settings),
        instructions=TRIAGE_INSTRUCTIONS,
        output_schema=Triage,
        db=db,
    )
