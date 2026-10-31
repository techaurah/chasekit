from datetime import date
from decimal import Decimal

import pytest

from chasekit.sources.base import SourceNotConfiguredError
from chasekit.sources.csv_source import CsvSource
from chasekit.sources.invoice_ninja import InvoiceNinjaSource

HEADER = (
    "invoice_number,client_name,client_email,contact_name,amount,"
    "currency,issue_date,due_date,status,jurisdiction\n"
)


def write_csv(tmp_path, rows: str):
    path = tmp_path / "invoices.csv"
    path.write_text(HEADER + rows, encoding="utf-8")
    return path


def test_parses_rows(tmp_path):
    path = write_csv(
        tmp_path,
        "INV-1,Acme Ltd,billing@acme.example,Jo,1000.50,GBP,2026-01-01,2026-01-15,unpaid,UK\n",
    )
    invoices = CsvSource(path).load()
    assert len(invoices) == 1
    inv = invoices[0]
    assert inv.number == "INV-1"
    assert inv.amount == Decimal("1000.50")
    assert inv.currency == "GBP"
    assert inv.due_date == date(2026, 1, 15)
    assert inv.paid is False
    assert inv.jurisdiction == "UK"


def test_paid_status_detected_case_insensitive(tmp_path):
    path = write_csv(
        tmp_path,
        "INV-2,Acme Ltd,billing@acme.example,Jo,10,GBP,2026-01-01,2026-01-15,PAID,UK\n",
    )
    assert CsvSource(path).load()[0].paid is True


def test_missing_column_reports_clearly(tmp_path):
    path = tmp_path / "bad.csv"
    path.write_text("invoice_number,amount\nINV-1,10\n", encoding="utf-8")
    with pytest.raises(ValueError, match="missing required columns"):
        CsvSource(path).load()


def test_missing_file_reports_clearly(tmp_path):
    with pytest.raises(SourceNotConfiguredError, match="not found"):
        CsvSource(tmp_path / "nope.csv").load()


def test_invoice_ninja_without_credentials_errors_clearly(monkeypatch):
    monkeypatch.delenv("CHASEKIT_INVOICE_NINJA_URL", raising=False)
    monkeypatch.delenv("CHASEKIT_INVOICE_NINJA_TOKEN", raising=False)
    source = InvoiceNinjaSource(base_url="", api_token="")
    with pytest.raises(SourceNotConfiguredError, match="not configured"):
        source.load()
