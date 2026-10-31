"""CSV invoice source. Fully working, no credentials needed.

Required columns:
    invoice_number, client_name, client_email, amount, currency, due_date
Optional columns:
    contact_name, issue_date, status, jurisdiction

Dates are ISO format (YYYY-MM-DD). `status` counts as paid when it is
"paid" in any case; anything else, including blank, is treated as
unpaid. `jurisdiction` is UK, EU, or US; blank uses the configured
default. See docs/sources.md for the full format.
"""

from __future__ import annotations

import csv
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

from ..models import Invoice
from .base import SourceNotConfiguredError

REQUIRED_COLUMNS = {
    "invoice_number",
    "client_name",
    "client_email",
    "amount",
    "currency",
    "due_date",
}


class CsvSource:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def load(self) -> list[Invoice]:
        if not self.path.exists():
            raise SourceNotConfiguredError(f"CSV file not found: {self.path}")
        invoices: list[Invoice] = []
        with self.path.open(newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            missing = REQUIRED_COLUMNS - set(reader.fieldnames or [])
            if missing:
                raise ValueError(
                    f"CSV is missing required columns: {', '.join(sorted(missing))}. "
                    f"Required: {', '.join(sorted(REQUIRED_COLUMNS))}."
                )
            for line, row in enumerate(reader, start=2):
                invoices.append(self._parse_row(row, line))
        return invoices

    @staticmethod
    def _parse_row(row: dict, line: int) -> Invoice:
        def field(name: str) -> str:
            return (row.get(name) or "").strip()

        try:
            amount = Decimal(field("amount").replace(",", ""))
        except InvalidOperation as exc:
            raise ValueError(f"Line {line}: invalid amount '{field('amount')}'") from exc
        try:
            due_date = date.fromisoformat(field("due_date"))
            issue_raw = field("issue_date")
            issue_date = date.fromisoformat(issue_raw) if issue_raw else None
        except ValueError as exc:
            raise ValueError(f"Line {line}: dates must be YYYY-MM-DD ({exc})") from exc
        return Invoice(
            number=field("invoice_number"),
            client_name=field("client_name"),
            client_email=field("client_email"),
            contact_name=field("contact_name"),
            amount=amount,
            currency=field("currency").upper(),
            issue_date=issue_date,
            due_date=due_date,
            paid=field("status").lower() == "paid",
            jurisdiction=field("jurisdiction").upper(),
        )
