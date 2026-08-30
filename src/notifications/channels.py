from notifications.base import NotificationChannel
import smtplib
from email.message import EmailMessage
import logging
from notifications.base import LoggingMixin, RetryMixin

logger = logging.getLogger(__name__)


class ConsoleChannel(NotificationChannel):
    """Prints the hand-off notice to stdout — useful for local runs/demos."""

    def send(self, message: str) -> bool:
        print(f"[human hand-off] {message}")
        return True


class EmailChannel(NotificationChannel):
    """Sends the hand-off notice by e-mail over SMTP."""

    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        from_addr: str,
        to_addr: str,
        use_tls: bool = True,
    ) -> None:
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.from_addr = from_addr
        self.to_addr = to_addr
        self.use_tls = use_tls

    def send(self, message: str) -> bool:
        msg = EmailMessage()
        msg["Subject"] = "Hand-off do konsultanta"
        msg["From"] = self.from_addr
        msg["To"] = self.to_addr
        msg.set_content(message)

        try:
            with smtplib.SMTP(self.host, self.port) as smtp:
                if self.use_tls:
                    smtp.starttls()
                if self.username:
                    smtp.login(self.username, self.password)
                smtp.send_message(msg)
        except (OSError, smtplib.SMTPException) as exc:
            logger.warning("e-mail to %s failed: %s", self.to_addr, exc)
            return False
        return True

class ReliableEmailChannel(LoggingMixin, RetryMixin, EmailChannel):
    """E-mail channel with logging and automatic retries.

    Multiple inheritance composes three single-purpose classes; MRO
    (``ReliableEmailChannel.__mro__``) determines call order:
    ``LoggingMixin.send`` -> ``RetryMixin.send`` -> ``EmailChannel.send``.
    """