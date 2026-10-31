"""Dry-run sender: captures what would be sent, sends nothing.

This is the default sender in v0.1 and the one the demo and tests use.
Captured messages stay in memory on `.sent` so callers (and tests) can
inspect exactly what a batch contained.
"""

from __future__ import annotations

from .base import OutboundMessage


class DryRunSender:
    def __init__(self) -> None:
        self.sent: list[OutboundMessage] = []

    def send(self, message: OutboundMessage) -> None:
        self.sent.append(message)
