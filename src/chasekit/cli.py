"""Command line interface.

    chasekit plan   --csv invoices.csv [--as-of YYYY-MM-DD]
    chasekit run    --csv invoices.csv [--mode dry-run|approve] [--yes]
    chasekit report --csv invoices.csv [--as-of YYYY-MM-DD]
    chasekit plan   --source invoice-ninja          (needs env config)

Safety posture: `plan` never sends and never writes. `run` defaults to
dry-run. `--mode approve` sends real email through SMTP and asks for an
interactive confirmation unless `--yes` is passed.
"""

from __future__ import annotations

import argparse
import sys
from datetime import date
from decimal import Decimal

from .config import Settings
from .engine import ChaseEngine
from .interest import build_packs
from .models import format_money
from .senders.dryrun import DryRunSender
from .senders.email import EmailSender, SmtpConfig
from .sources.base import InvoiceSource, SourceNotConfiguredError
from .sources.csv_source import CsvSource
from .sources.invoice_ninja import InvoiceNinjaSource
from .store import ChaseStore


def _settings_from_args(args: argparse.Namespace) -> Settings:
    settings = Settings.from_env()
    settings.business_name = args.business_name or settings.business_name
    settings.default_jurisdiction = args.jurisdiction.upper()
    settings.uk_base_rate = Decimal(args.uk_base_rate)
    settings.eu_reference_rate = Decimal(args.eu_reference_rate)
    settings.us_annual_rate = Decimal(args.us_rate)
    settings.us_fixed_fee = Decimal(args.us_fee)
    settings.db_path = args.db
    return settings


def _source_from_args(args: argparse.Namespace) -> InvoiceSource:
    if args.source == "invoice-ninja":
        return InvoiceNinjaSource()
    if not args.csv:
        raise SourceNotConfiguredError(
            "No invoice source given. Pass --csv invoices.csv, or "
            "--source invoice-ninja with its environment variables set."
        )
    return CsvSource(args.csv)


def _print_plan(actions, heading: str) -> None:
    print(heading)
    if not actions:
        print("  Nothing to chase: no overdue invoice is due a new stage.")
        return
    for action in actions:
        invoice = action.invoice
        print(
            f"  {invoice.number:<10} {invoice.client_name:<28} "
            f"stage {action.stage} ({action.stage_name}), "
            f"{action.days_overdue} days overdue, "
            f"interest {format_money(action.interest.interest, invoice.currency)}, "
            f"fee {format_money(action.interest.fixed_fee, invoice.currency)}, "
            f"total {format_money(action.interest.total_due, invoice.currency)}"
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="chasekit",
        description="Chase overdue invoices: statutory interest, tone-ladder "
        "templates, dry-run by default. Creates no invoices, does no accounting.",
    )
    parser.add_argument("--csv", help="Path to a CSV invoice export (see docs/sources.md)")
    parser.add_argument(
        "--source",
        choices=["csv", "invoice-ninja"],
        default="csv",
        help="Invoice source (default: csv)",
    )
    parser.add_argument("--db", default="chasekit.db", help="SQLite chase log path")
    parser.add_argument("--business-name", default="", help="Your business name for templates")
    parser.add_argument(
        "--jurisdiction",
        default="UK",
        help="Default jurisdiction pack for invoices without one: UK, EU, or US",
    )
    parser.add_argument("--uk-base-rate", default="4.00", help="Bank of England base rate, percent")
    parser.add_argument("--eu-reference-rate", default="2.15", help="EU reference rate, percent")
    parser.add_argument("--us-rate", default="0", help="US configured annual rate, percent")
    parser.add_argument("--us-fee", default="0", help="US configured fixed fee")
    parser.add_argument("--as-of", default="", help="Run as of this date (YYYY-MM-DD)")

    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("plan", help="Show what would be chased. Sends and writes nothing.")
    run_parser = sub.add_parser("run", help="Execute a chase run.")
    run_parser.add_argument(
        "--mode",
        choices=["dry-run", "approve"],
        default="dry-run",
        help="dry-run (default) sends nothing; approve sends for real",
    )
    run_parser.add_argument(
        "--yes",
        action="store_true",
        help="Skip the interactive confirmation in approve mode",
    )
    sub.add_parser("report", help="Outstanding totals by age band and by client.")

    args = parser.parse_args(argv)
    as_of = date.fromisoformat(args.as_of) if args.as_of else date.today()
    settings = _settings_from_args(args)

    try:
        source = _source_from_args(args)
        store = ChaseStore(settings.db_path)
        if args.command == "report":
            engine = ChaseEngine(source, store, settings, packs=build_packs(settings))
            print(engine.report(as_of))
            return 0

        if args.command == "plan":
            engine = ChaseEngine(source, store, settings, packs=build_packs(settings))
            actions = engine.plan(as_of)
            _print_plan(actions, f"Chase plan as of {as_of.isoformat()} (nothing sent):")
            return 0

        # run
        approve = args.mode == "approve"
        if approve:
            sender = EmailSender(SmtpConfig.from_env())
            engine = ChaseEngine(source, store, settings, sender=sender,
                                 packs=build_packs(settings))
            actions = engine.plan(as_of)
            _print_plan(actions, "The following messages will be SENT:")
            if actions and not args.yes:
                answer = input("Type YES to send this batch: ").strip()
                if answer != "YES":
                    print("Aborted. Nothing was sent.")
                    return 0
            sent = engine.run(as_of, approve=True)
            print(f"Sent {len(sent)} message(s). Recorded in {settings.db_path}.")
            return 0

        engine = ChaseEngine(source, store, settings, sender=DryRunSender(),
                             packs=build_packs(settings))
        actions = engine.run(as_of, approve=False)
        _print_plan(actions, f"Dry run as of {as_of.isoformat()} (nothing sent):")
        print(
            "DRY RUN: no email was sent. Review the batch, then re-run with "
            "--mode approve to send it."
        )
        return 0
    except (SourceNotConfiguredError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
