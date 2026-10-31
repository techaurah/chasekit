"""United States jurisdiction pack.

There is no US federal statute setting late-payment interest on
ordinary business-to-business invoices. What a creditor can charge
comes from the contract terms the parties agreed, or from state law
(which varies: some states have prompt-payment acts covering specific
sectors such as construction or government contracts, and state
default interest rates differ).

ChaseKit therefore ships an honest default: an annual rate of 0% and a
fixed fee of $0. Set `us_annual_rate` and `us_fixed_fee` in the
configuration to your contracted terms or your state's figure, and
ChaseKit will calculate and state them. Nothing is invented on your
behalf.
"""

from __future__ import annotations

from decimal import Decimal

from .base import JurisdictionPack


class USPack(JurisdictionPack):
    key = "US"
    name = "United States"

    def __init__(
        self,
        annual_rate: Decimal = Decimal(0),
        fixed_fee: Decimal = Decimal(0),
    ) -> None:
        self.annual_rate = annual_rate
        self.fixed_fee = fixed_fee

    def annual_rate_percent(self) -> Decimal:
        return self.annual_rate

    def fixed_fee_for(self, principal: Decimal) -> Decimal:
        return self.fixed_fee

    def basis(self) -> str:
        if self.annual_rate == 0 and self.fixed_fee == 0:
            return (
                "No late-payment interest or fee applied: the United States "
                "has no federal statutory rate, and none is configured"
            )
        return (
            f"Contracted or state-configured late-payment terms "
            f"({self.annual_rate}% per year, fixed fee as configured); the "
            "United States has no federal statutory rate"
        )
