"""The v0.1 safety contract: dry-run is the default, a dry run sends
nothing real and blocks nothing, and the CLI says so out loud."""

from datetime import date

from chasekit.cli import main
from chasekit.config import Settings
from chasekit.engine import ChaseEngine
from chasekit.senders.dryrun import DryRunSender
from chasekit.sources.csv_source import CsvSource
from chasekit.store import ChaseStore

AS_OF = date(2026, 1, 31)
CSV = """invoice_number,client_name,client_email,contact_name,amount,currency,issue_date,due_date,status,jurisdiction
INV-1,Maple Design Studio,billing@maple.example,Jo Parker,850.00,GBP,2026-01-20,2026-01-27,unpaid,UK
"""


def build(tmp_path):
    csv_path = tmp_path / "invoices.csv"
    csv_path.write_text(CSV, encoding="utf-8")
    store = ChaseStore(tmp_path / "chase.db")
    sender = DryRunSender()
    engine = ChaseEngine(CsvSource(csv_path), store, Settings(), sender=sender)
    return engine, store, sender


def test_dry_run_records_but_does_not_block(tmp_path):
    engine, store, sender = build(tmp_path)
    actions = engine.run(AS_OF, approve=False)
    assert len(actions) == 1
    assert actions[0].status == "dry_run"
    # The dry-run sender captured exactly what would have gone out.
    assert len(sender.sent) == 1
    assert sender.sent[0].to == "billing@maple.example"
    # But nothing counts as sent, so the stage is still plannable.
    assert store.has_sent("INV-1", 1) is False
    assert len(engine.plan(AS_OF)) == 1
    history = store.history("INV-1")
    assert history[0]["status"] == "dry_run"


def test_cli_run_defaults_to_dry_run(tmp_path, capsys):
    csv_path = tmp_path / "invoices.csv"
    csv_path.write_text(CSV, encoding="utf-8")
    code = main(
        [
            "--csv", str(csv_path),
            "--db", str(tmp_path / "cli.db"),
            "--as-of", "2026-01-31",
            "run",
        ]
    )
    out = capsys.readouterr().out
    assert code == 0
    assert "DRY RUN: no email was sent" in out


def test_cli_plan_writes_nothing(tmp_path, capsys):
    csv_path = tmp_path / "invoices.csv"
    csv_path.write_text(CSV, encoding="utf-8")
    db = tmp_path / "plan.db"
    code = main(
        ["--csv", str(csv_path), "--db", str(db), "--as-of", "2026-01-31", "plan"]
    )
    out = capsys.readouterr().out
    assert code == 0
    assert "INV-1" in out
    store = ChaseStore(db)
    assert store.history("INV-1") == []
