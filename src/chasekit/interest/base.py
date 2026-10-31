"""Shared interest maths.

Interest is simple interest on the invoice principal:
    interest = principal * (annual rate / 100) * days_overdue / 365
rounded half-up to cents. Both the UK Act and the EU Directive accrue
interest daily on this basis; neither compounds.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

CENTS = Decimal("0.01")


def simple_interest(principal: Decimal, annual_rate_percent: Decimal, days: int) -> Decimal:
    raw = principal * (annual_rate_percent / Decimal(100)) * Decimal(days) / Decimal(365)
    return raw.quantize(CENTS, rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class InterestResult:
    principal: Decimal
    days_overdue: int
    annual_rate_percent: Decimal
    interest: Decimal
    fixed_fee: Decimal
    basis: str  # human-readable statement of the legal basis used

    @property
    def total_due(self) -> Decimal:
        return self.principal + self.interest + self.fixed_fee


class JurisdictionPack:
    """One country's statutory late-payment rules."""

    key: str = ""
    name: str = ""

    def annual_rate_percent(self) -> Decimal:
        raise NotImplementedError

    def fixed_fee_for(self, principal: Decimal) -> Decimal:
        raise NotImplementedError

    def basis(self) -> str:
        raise NotImplementedError

    def calculate(self, principal: Decimal, days_overdue: int) -> InterestResult:
        if days_overdue <= 0:
            return InterestResult(
                principal=principal,
                days_overdue=0,
                annual_rate_percent=self.annual_rate_percent(),
                interest=Decimal("0.00"),
                fixed_fee=Decimal("0.00"),
                basis=self.basis(),
            )
        return InterestResult(
            principal=principal,
            days_overdue=days_overdue,
            annual_rate_percent=self.annual_rate_percent(),
            interest=simple_interest(principal, self.annual_rate_percent(), days_overdue),
            fixed_fee=self.fixed_fee_for(principal),
            basis=self.basis(),
        )
