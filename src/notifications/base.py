from __future__ import annotations

import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class NotificationChannel(ABC):
    """Contract for anything that can alert a human consultant."""

    @abstractmethod
    def send(self, message: str) -> bool:
        """Sends `message`, returns whether it was delivered."""


class LoggingMixin:
    """Logs every send attempt, then delegates to the next class in the MRO."""

    def send(self, message: str) -> bool:
        logger.info("sending via %s: %s", type(self).__name__, message)
        delivered = super().send(message)
        logger.info("delivered=%s", delivered)
        return delivered


class RetryMixin:
    """Retries `send` up to `max_attempts` times before giving up."""

    max_attempts: int = 3

    def send(self, message: str) -> bool:
        for attempt in range(1, self.max_attempts + 1):
            if super().send(message):
                return True
            logger.warning("attempt %s/%s failed", attempt, self.max_attempts)
        return False
