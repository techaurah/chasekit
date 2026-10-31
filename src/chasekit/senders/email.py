"""SMTP email sender, used only on the approve path.

Implemented with the standard library (smtplib) so ChaseKit keeps zero
runtime dependencies. Configure via environment variables; see
.env.example. Use an app password or a dedicated mailbox, never a main
account password.
"""

from __future__ import annotations

import os
import smtplib
from dataclasses import dataclass
from email.message import EmailMessage

from ..sources.base import SourceNotConfiguredError
from .base import OutboundMessage


@dataclass
class SmtpConfig:
    host: str = ""
    port: int = 587
    username: str = ""
    password: str = ""
    from_address: str = ""
    starttls: bool = True

    @classmethod
    def from_env(cls) -> SmtpConfig:
        return cls(
            host=os.environ.get("CHASEKIT_SMTP_HOST", ""),
            port=int(os.environ.get("CHASEKIT_SMTP_PORT", "587")),
            username=os.environ.get("CHASEKIT_SMTP_USERNAME", ""),
            password=os.environ.get("CHASEKIT_SMTP_PASSWORD", ""),
            from_address=os.environ.get("CHASEKIT_SMTP_FROM", ""),
            starttls=os.environ.get("CHASEKIT_SMTP_STARTTLS", "1") == "1",
        )

    def require_complete(self) -> None:
        missing = [
            name
            for name, value in (
                ("CHASEKIT_SMTP_HOST", self.host),
                ("CHASEKIT_SMTP_FROM", self.from_address),
            )
            if not value
        ]
        if missing:
            raise SourceNotConfiguredError(
                "Approve mode sends real email and needs SMTP configuration. "
                f"Missing: {', '.join(missing)}. See .env.example, or use "
                "dry-run mode (the default) to preview the batch instead."
            )


class EmailSender:
    def __init__(self, config: SmtpConfig) -> None:
        config.require_complete()
        self.config = config

    def send(self, message: OutboundMessage) -> None:
        email = EmailMessage()
        email["From"] = self.config.from_address
        email["To"] = message.to
        email["Subject"] = message.subject
        email.set_content(message.body)
        with smtplib.SMTP(self.config.host, self.config.port, timeout=30) as smtp:
            if self.config.starttls:
                smtp.starttls()
            if self.config.username:
                smtp.login(self.config.username, self.config.password)
            smtp.send_message(email)
