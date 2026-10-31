"""The chasing engine: detection, escalation stages, rendering, sending.

Stage state machine, driven purely by days overdue:

    stage 1  friendly reminder     days overdue >= 1
    stage 2  firm reminder         days overdue >= 14
    stage 3  final notice          days overdue >= 28
    stage 4  escalation handoff    days overdue >= 42

An invoice is due the highest stage its age reaches. Each stage is
sent at most once per invoice: the SQLite chase log is checked before
planning and written after every action. A dry run is recorded as
status "dry_run" and never blocks a later real send.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from importlib import resources

from .config import Settings
from .interest import InterestResult, JurisdictionPack, build_packs, get_pack
from .models import Invoice, format_money
from .senders.base import OutboundMessage, Sender
from .senders.dryrun import DryRunSender
from .sources.base import InvoiceSource
from .store import ChaseStore

STAGES: dict[int, tuple[str, int, str]] = {
    # stage -> (name, minimum days overdue, template file)
    1: ("friendly", 1, "stage1-friendly.md"),
    2: ("firm", 14, "stage2-firm.md"),
    3: ("final", 28, "stage3-final.md"),
    4: ("escalation", 42, "stage4-escalation.md"),
}

AGE_BANDS: list[tuple[str, int, int | None]] = [
    ("1-7 days", 1, 7),
    ("8-14 days", 8, 14),
    ("15-30 days", 15, 30),
    ("31-60 days", 31, 60),
    ("61+ days", 61, None),
]


def stage_for_days(days_overdue: int) -> int:
    stage = 0
    for number, (_, threshold, _) in sorted(STAGES.items()):
        if days_overdue >= threshold:
            stage = number
    return stage


def age_band(days_overdue: int) -> str:
    for label, low, high in AGE_BANDS:
        if days_overdue >= low and (high is None or days_overdue <= high):
            return label
    return "not due"


def load_template(stage: int, language: str = "en") -> tuple[str, str]:
    filename = STAGES[stage][2]
    resource = resources.files("chasekit").joinpath("templates", language, filename)
    text = resource.read_text(encoding="utf-8")
    subject, _, body = text.partition("\n\n")
    subject = subject.removeprefix("Subject:").strip()
    return subject, body.strip()


def render(template: str, context: dict[str, str]) -> str:
    rendered = template
    for key, value in context.items():
        rendered = rendered.replace("{{" + key + "}}", value)
    return rendered


@dataclass
class ChaseAction:
    invoice: Invoice
    stage: int
    stage_name: str
    days_overdue: int
    interest: InterestResult
    subject: str
    body: str
    status: str = "planned"  # planned | dry_run | sent


class ChaseEngine:
    def __init__(
        self,
        source: InvoiceSource,
        store: ChaseStore,
        settings: Settings | None = None,
        sender: Sender | None = None,
        packs: dict[str, JurisdictionPack] | None = None,
    ) -> None:
        self.source = source
        self.store = store
        self.settings = settings or Settings()
        self.sender = sender or DryRunSender()
        self.packs = packs or build_packs(self.settings)

    def _interest_for(self, invoice: Invoice, as_of: date) -> InterestResult:
        key = invoice.jurisdiction or self.settings.default_jurisdiction
        pack = get_pack(self.packs, key)
        return pack.calculate(invoice.amount, invoice.days_overdue(as_of))

    def _context(
        self, invoice: Invoice, result: InterestResult, days: int
    ) -> dict[str, str]:
        currency = invoice.currency
        return {
            "business_name": self.settings.business_name,
            "client_name": invoice.client_name,
            "contact_name": invoice.contact_name or invoice.client_name,
            "invoice_number": invoice.number,
            "amount": format_money(invoice.amount, currency),
            "interest_amount": format_money(result.interest, currency),
            "fixed_fee": format_money(result.fixed_fee, currency),
            "total_due": format_money(result.total_due, currency),
            "due_date": invoice.due_date.isoformat(),
            "days_overdue": str(days),
            "annual_rate_percent": str(result.annual_rate_percent),
            "interest_basis": result.basis,
        }

    def plan(self, as_of: date) -> list[ChaseAction]:
        """What would be chased today. Sends nothing, writes nothing."""
        actions: list[ChaseAction] = []
        for invoice in self.source.load():
            if not invoice.is_overdue(as_of):
                continue
            days = invoice.days_overdue(as_of)
            stage = stage_for_days(days)
            if stage == 0 or self.store.has_sent(invoice.number, stage):
                continue
            result = self._interest_for(invoice, as_of)
            context = self._context(invoice, result, days)
            subject_template, body_template = load_template(stage)
            actions.append(
                ChaseAction(
                    invoice=invoice,
                    stage=stage,
                    stage_name=STAGES[stage][0],
                    days_overdue=days,
                    interest=result,
                    subject=render(subject_template, context),
                    body=render(body_template, context),
                )
            )
        return actions

    def run(self, as_of: date, approve: bool = False) -> list[ChaseAction]:
        """Execute the plan.

        approve=False is a dry run: messages go to the (dry-run) sender,
        are logged as "dry_run", and block nothing. approve=True sends
        through the configured sender and logs "sent", which blocks any
        repeat of that stage for that invoice forever.
        """
        actions = self.plan(as_of)
        for action in actions:
            message = OutboundMessage(
                to=action.invoice.client_email,
                subject=action.subject,
                body=action.body,
                invoice_number=action.invoice.number,
                stage=action.stage,
            )
            if approve:
                self.sender.send(message)
                action.status = "sent"
            else:
                if isinstance(self.sender, DryRunSender):
                    self.sender.send(message)
                action.status = "dry_run"
            self.store.record(
                action.invoice.number,
                action.invoice.client_email,
                action.stage,
                action.status,
                action.subject,
                action.body,
            )
        return actions

    def report(self, as_of: date) -> str:
        """Outstanding totals by age band and by client, as text."""
        invoices = [i for i in self.source.load() if i.is_overdue(as_of)]
        lines = [f"Outstanding report as of {as_of.isoformat()}", ""]
        if not invoices:
            lines.append("Nothing overdue. Every unpaid invoice is within terms.")
            return "\n".join(lines)

        lines.append("By age band:")
        for label, _, _ in AGE_BANDS:
            band = [i for i in invoices if age_band(i.days_overdue(as_of)) == label]
            if not band:
                continue
            totals = self._totals_by_currency(band, as_of)
            lines.append(f"  {label:<10} {len(band)} invoice(s): {totals}")
        lines.append("")
        lines.append("By client:")
        clients: dict[str, list[Invoice]] = {}
        for invoice in invoices:
            clients.setdefault(invoice.client_name, []).append(invoice)
        for client in sorted(clients):
            rows = clients[client]
            totals = self._totals_by_currency(rows, as_of)
            oldest = max(i.days_overdue(as_of) for i in rows)
            lines.append(f"  {client}: {len(rows)} invoice(s), oldest {oldest} days. {totals}")
        lines.append("")
        grand = self._totals_by_currency(invoices, as_of, include_interest=True)
        lines.append(f"Total outstanding (principal + interest + fees): {grand}")
        return "\n".join(lines)

    def _totals_by_currency(
        self, invoices: list[Invoice], as_of: date, include_interest: bool = True
    ) -> str:
        per_currency: dict[str, object] = {}
        for invoice in invoices:
            result = self._interest_for(invoice, as_of)
            total = result.total_due if include_interest else invoice.amount
            per_currency[invoice.currency] = per_currency.get(
                invoice.currency, result.principal * 0
            ) + total
        return "; ".join(
            f"{format_money(amount, currency)}"
            for currency, amount in sorted(per_currency.items())
        )
