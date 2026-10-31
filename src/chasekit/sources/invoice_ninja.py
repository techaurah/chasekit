"""Invoice Ninja API source.

Status in v0.1: implemented behind the source interface, but it needs
a real Invoice Ninja instance and API token, so it is NOT exercised by
the automated tests or the demo (the CSV source is). If the credentials
are not configured, `load()` raises SourceNotConfiguredError with
instructions instead of failing obscurely. That limitation is stated
here and in docs/sources.md rather than hidden.

Configuration (environment variables):
    CHASEKIT_INVOICE_NINJA_URL    e.g. https://ninja.example.com
    CHASEKIT_INVOICE_NINJA_TOKEN  API token from Invoice Ninja admin

Field mapping follows the standard Invoice Ninja v5 API response for
GET /api/v1/invoices with client data included: number, amount,
due_date, status_id (4 = paid), and the embedded client's name and
first contact email.
"""

from __future__ import annotations

import json
import os
import urllib.request
from datetime import date
from decimal import Decimal

from ..models import Invoice
from .base import SourceNotConfiguredError

PAID_STATUS_ID = 4


class InvoiceNinjaSource:
    def __init__(
        self,
        base_url: str | None = None,
        api_token: str | None = None,
        currency: str | None = None,
    ) -> None:
        self.base_url = (base_url or os.environ.get("CHASEKIT_INVOICE_NINJA_URL", "")).rstrip("/")
        self.api_token = api_token or os.environ.get("CHASEKIT_INVOICE_NINJA_TOKEN", "")
        # The v5 API returns a numeric currency_id, not an ISO code, so
        # the account currency is taken as configuration instead of
        # guessed. Most Invoice Ninja accounts bill in one currency.
        self.currency = (
            currency or os.environ.get("CHASEKIT_INVOICE_NINJA_CURRENCY", "USD")
        ).upper()

    def load(self) -> list[Invoice]:
        if not self.base_url or not self.api_token:
            raise SourceNotConfiguredError(
                "Invoice Ninja source is not configured. Set "
                "CHASEKIT_INVOICE_NINJA_URL and CHASEKIT_INVOICE_NINJA_TOKEN "
                "(create a token in Invoice Ninja under Settings, then API "
                "Tokens), or use the CSV source instead: "
                "chasekit plan --csv invoices.csv"
            )
        url = f"{self.base_url}/api/v1/invoices?include=client&per_page=200"
        request = urllib.request.Request(
            url,
            headers={"X-Api-Token": self.api_token, "Accept": "application/json"},
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
        return [self._parse(item) for item in payload.get("data", [])]

    def _parse(self, item: dict) -> Invoice:
        client = item.get("client") or {}
        contacts = client.get("contacts") or []
        email = ""
        if contacts:
            email = contacts[0].get("email", "") or ""
        return Invoice(
            number=str(item.get("number", "")),
            client_name=client.get("display_name") or client.get("name", ""),
            client_email=email,
            contact_name="",
            amount=Decimal(str(item.get("amount", "0"))),
            currency=self.currency,
            due_date=date.fromisoformat(item["due_date"]),
            paid=int(item.get("status_id", 0)) == PAID_STATUS_ID,
            jurisdiction="",
        )
