"""European Union jurisdiction pack.

Statute: Directive 2011/7/EU of 16 February 2011 on combating late
payment in commercial transactions, as implemented by each member
state's national law.

- Interest for late payment: the reference rate plus at least 8
  percentage points (Article 2(2) and Article 3). The reference rate is
  the European Central Bank's main refinancing operations rate for
  euro-area states (the rate in force on 1 January or 1 July for the
  following six months), or the national central bank rate for member
  states outside the euro. ChaseKit takes the reference rate as
  configuration so a pack user can set their member state's figure.
- Fixed compensation: the creditor is entitled to a minimum fixed sum
  of €40 as compensation for recovery costs, on top of interest,
  without the need for a reminder (Article 6(1)). Reasonable recovery
  costs above €40 may also be claimable; ChaseKit calculates the €40
  statutory minimum only.

ChaseKit uses the Directive's floor. Member-state implementations can
be more favourable to the creditor. Applies where the invoice currency
is EUR.
"""

from __future__ import annotations

from decimal import Decimal

from .base import JurisdictionPack

STATUTORY_UPLIFT = Decimal(8)
MINIMUM_FIXED_FEE = Decimal("40.00")


class EUPack(JurisdictionPack):
    key = "EU"
    name = "European Union"

    def __init__(self, reference_rate: Decimal = Decimal("2.15")) -> None:
        self.reference_rate = reference_rate

    def annual_rate_percent(self) -> Decimal:
        return self.reference_rate + STATUTORY_UPLIFT

    def fixed_fee_for(self, principal: Decimal) -> Decimal:
        return MINIMUM_FIXED_FEE

    def basis(self) -> str:
        return (
            f"Reference rate ({self.reference_rate}%) + 8 percentage points, "
            "and the EUR 40 minimum fixed compensation, under Directive "
            "2011/7/EU on combating late payment in commercial transactions"
        )
