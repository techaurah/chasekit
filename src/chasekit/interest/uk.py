"""United Kingdom jurisdiction pack.

Statute: Late Payment of Commercial Debts (Interest) Act 1998
(as amended, including by the Late Payment of Commercial Debts
Regulations 2013).

- Statutory interest rate: the Bank of England base rate (the
  "reference rate") plus 8 percentage points (Act, section 6). For a
  debt whose interest period starts in January to June, the reference
  rate is the base rate in force at the previous 31 December; for July
  to December it is the rate in force at the previous 30 June.
  ChaseKit takes the applicable base rate as configuration so the
  correct half-year figure is used.
- Fixed compensation for recovery costs (Act, section 5A), on top of
  interest, scaled by the size of the debt:
      debt under £1,000          -> £40
      debt £1,000 to £9,999.99   -> £70
      debt £10,000 or more       -> £100
- Statutory interest applies to business-to-business debts where the
  contract does not provide a substantial remedy of its own. ChaseKit
  calculates the statutory figure; whether it applies to a specific
  contract is the user's legal position to confirm.

Applies where the invoice currency is GBP.
"""

from __future__ import annotations

from decimal import Decimal

from .base import JurisdictionPack

STATUTORY_UPLIFT = Decimal(8)


class UKPack(JurisdictionPack):
    key = "UK"
    name = "United Kingdom"

    def __init__(self, base_rate: Decimal = Decimal("4.00")) -> None:
        self.base_rate = base_rate

    def annual_rate_percent(self) -> Decimal:
        return self.base_rate + STATUTORY_UPLIFT

    def fixed_fee_for(self, principal: Decimal) -> Decimal:
        if principal < Decimal(1000):
            return Decimal("40.00")
        if principal < Decimal(10000):
            return Decimal("70.00")
        return Decimal("100.00")

    def basis(self) -> str:
        return (
            f"Bank of England base rate ({self.base_rate}%) + 8% statutory interest, "
            "and fixed compensation under the Late Payment of Commercial Debts "
            "(Interest) Act 1998"
        )
