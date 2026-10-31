"""The invoice source interface.

A source loads invoices from wherever a business already keeps them.
Implementing a new source (Stripe, Akaunting, JSON) means implementing
`load()` and nothing else: detection, interest, templates, and sending
all work unchanged.
"""

from __future__ import annotations

from typing import Protocol

from ..models import Invoice


class SourceNotConfiguredError(RuntimeError):
    """Raised when a source is used without the credentials it needs."""


class InvoiceSource(Protocol):
    def load(self) -> list[Invoice]:
        """Return all invoices, paid and unpaid. The engine filters."""
        ...
