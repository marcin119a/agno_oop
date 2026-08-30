from __future__ import annotations

from typing import Callable, List

from agno.tools import Toolkit

from agents.faq.knowledge_base import FAQ
from notifications import HandoffNotifier


class HandoffTools(Toolkit):
    """Notifies a human consultant and produces the reply for the passenger.

    Mirrors the `_human_handoff` step of the Workflow in `handoff.py` — the
    same notification and the same canned reply — but exposed as a tool, so
    an *agent* can run it. That is what a `Team` needs: its members must be
    agents, not plain functions.
    """

    def __init__(self, notifier: HandoffNotifier | None = None, **kwargs):
        self.notifier = notifier or HandoffNotifier()
        tools: List[Callable] = [self.notify_consultant]
        super().__init__(name="handoff", tools=tools, **kwargs)

    def notify_consultant(self, question: str, reason: str) -> str:
        """Passes the passenger's question to a human consultant.

        Args:
            question: The passenger's message, verbatim.
            reason: Short reason why a human is needed, e.g.
                "status konkretnego lotu" or "reklamacja biletu".

        Returns:
            The reply to send to the passenger, word for word.
        """
        self.notifier.notify(f"Hand-off needed ({reason}): {question}")
        return f"To pytanie wymaga kontaktu z konsultantem ({reason}).\n\n{FAQ['helpline contact']}"
