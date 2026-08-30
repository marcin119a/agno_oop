
from __future__ import annotations

from dataclasses import dataclass, field

from notifications.base import NotificationChannel
from notifications.channels import ConsoleChannel, ReliableEmailChannel


@dataclass
class HandoffNotifier:
    """Notifies every configured channel about a hand-off.
    """

    channels: list[NotificationChannel] = field(default_factory=lambda: [ConsoleChannel()])

    def notify(self, message: str) -> int:
        """Sends `message` to every channel, returns how many delivered it."""
        return sum(channel.send(message) for channel in self.channels)

    @classmethod
    def from_settings(cls, settings) -> "HandoffNotifier":
        """Builds a notifier from `Settings`.

        E-mail over SMTP when `smtp_host` is set, otherwise the default
        (console-only) notifier, so callers keep working with no
        credentials configured.
        """
        if not settings.smtp_host:
            return cls()
        return cls(
            channels=[
                ReliableEmailChannel(
                    host=settings.smtp_host,
                    port=settings.smtp_port,
                    username=settings.smtp_username,
                    password=settings.smtp_password.get_secret_value(),
                    from_addr=settings.smtp_from,
                    to_addr=settings.smtp_to,
                    use_tls=settings.smtp_use_tls,
                )
            ]
        )
