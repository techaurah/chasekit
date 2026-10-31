"""The sender interface.

A sender delivers one rendered message. ChaseKit's safety rule lives
above this layer: the engine only calls a real sender on the approve
path. New channels (a different mail provider, a print-and-post
service) implement `send()` and nothing else.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class OutboundMessage:
    to: str
    subject: str
    body: str
    invoice_number: str
    stage: int


class Sender(Protocol):
    def send(self, message: OutboundMessage) -> None:
        """Deliver the message, or raise on failure."""
        ...
