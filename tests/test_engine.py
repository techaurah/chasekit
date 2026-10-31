from datetime import date

from chasekit.config import Settings
from chasekit.engine import ChaseEngine, stage_for_days
from chasekit.senders.dryrun import DryRunSender
from chasekit.sources.csv_source import CsvSource
from chasekit.store import ChaseStore

AS_OF = date(2026, 1, 31)
CSV = """invoice_number,client_name,client_email,contact_name,amount,currency,issue_date,due_date,status,jurisdiction
INV-1,Maple Design Studio,billing@maple.example,Jo Parker,850.00,GBP,2026-01-20,2026-01-27,unpaid,UK
INV-2,Brightpath Consulting,accounts@brightpath.example,Sam Reed,2400.00,GBP,2025-12-29,2026-01-15,unpaid,UK
INV-3,Koeln Media GmbH,buchhaltung@koeln.example,Frau Lindner,5000.00,EUR,2025-12-12,2026-01-02,unpaid,EU
INV-4,Hartley Construction,office@hartley.example,Dan Hartley,12000.00,GBP,2025-11-28,2025-12-15,unpaid,UK
INV-5,Studio Verde,admin@verde.example,Luca Bianchi,1750.00,EUR,2026-01-30,2026-02-10,unpaid,EU
INV-6,Northwind Traders,payables@northwind.example,Ada Cole,640.00,GBP,2025-12-18,2026-01-05,paid,UK
"""


def build(tmp_path):
    csv_path = tmp_path / "invoices.csv"
    csv_path.write_text(CSV, encoding="utf-8")
    store = ChaseStore(tmp_path / "chase.db")
    sender = DryRunSender()
    engine = ChaseEngine(
        CsvSource(csv_path),
        store,
        Settings(business_name="Bright Studio"),
        sender=sender,
    )
    return engine, store, sender


def test_stage_thresholds():
    assert stage_for_days(0) == 0
    assert stage_for_days(1) == 1
    assert stage_for_days(13) == 1
    assert stage_for_days(14) == 2
    assert stage_for_days(27) == 2
    assert stage_for_days(28) == 3
    assert stage_for_days(41) == 3
    assert stage_for_days(42) == 4
    assert stage_for_days(90) == 4


def test_plan_covers_each_stage_and_skips_clean_invoices(tmp_path):
    engine, _, _ = build(tmp_path)
    actions = engine.plan(AS_OF)
    by_number = {a.invoice.number: a for a in actions}
    assert set(by_number) == {"INV-1", "INV-2", "INV-3", "INV-4"}
    assert by_number["INV-1"].stage == 1  # 4 days
    assert by_number["INV-2"].stage == 2  # 16 days
    assert by_number["INV-3"].stage == 3  # 29 days
    assert by_number["INV-4"].stage == 4  # 47 days


def test_templates_render_with_correct_amounts(tmp_path):
    engine, _, _ = build(tmp_path)
    actions = {a.invoice.number: a for a in engine.plan(AS_OF)}
    inv4 = actions["INV-4"]
    assert "£12,000.00" in inv4.body
    assert "£185.42" in inv4.body
    assert "£100.00" in inv4.body
    assert "£12,285.42" in inv4.body
    assert "Late Payment of Commercial Debts" in inv4.body
    assert "Bright Studio" in inv4.body
    assert "{{" not in inv4.body
    inv3 = actions["INV-3"]
    assert "€5,080.32" in inv3.body
    assert "2011/7/EU" in inv3.body


def test_sent_stage_is_never_replanned(tmp_path):
    engine, store, _ = build(tmp_path)
    engine.run(AS_OF, approve=True)
    assert engine.plan(AS_OF) == []
    assert store.has_sent("INV-1", 1)


def test_report_includes_bands_and_clients(tmp_path):
    engine, _, _ = build(tmp_path)
    report = engine.report(AS_OF)
    assert "By age band:" in report
    assert "By client:" in report
    assert "Hartley Construction" in report
    assert "Total outstanding" in report
