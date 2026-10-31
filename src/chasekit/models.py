"""Core data model. Money is Decimal everywhere, never float."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

CURRENCY_SYMBOLS = {
    "GBP": "£",
    "EUR": "€",
    "USD": "$",
}


def currency_symbol(currency: str) -> str:
    return CURRENCY_SYMBOLS.get(currency.upper(), currency.upper() + " ")


def format_money(amount: Decimal, currency: str) -> str:
    return f"{currency_symbol(currency)}{amount:,.2f}"


@dataclass(frozen=True)
class Invoice:
    """One invoice as loaded from a source.

    `jurisdiction` is a pack key: "UK", "EU", or "US". An empty string
    means "use the configured default jurisdiction".
    """

    number: str
    client_name: str
    client_email: str
    amount: Decimal
    currency: str
    due_date: date
    contact_name: str = ""
    issue_date: date | None = None
    paid: bool = False
    jurisdiction: str = ""

    def days_overdue(self, as_of: date) -> int:
        return (as_of - self.due_date).days

    def is_overdue(self, as_of: date) -> bool:
        return not self.paid and self.days_overdue(as_of) > 0
