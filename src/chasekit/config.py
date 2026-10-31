"""Runtime settings. Rates are configuration, not constants, because
statutory reference rates change twice a year in both the UK and the EU.
The defaults below are documented starting points: verify the current
rate before relying on a figure (see docs/interest-rules.md)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Settings:
    business_name: str = "Your Business"
    default_jurisdiction: str = "UK"
    # UK: Bank of England base rate in force for the half-year.
    # 4.00% applied from August 2025; check bankofengland.co.uk.
    uk_base_rate: Decimal = Decimal("4.00")
    # EU: ECB main refinancing operations rate.
    # 2.15% applied from June 2025; check ecb.europa.eu.
    eu_reference_rate: Decimal = Decimal("2.15")
    # US: no federal statute. Zero unless your contract or state law
    # gives you a rate; set both values to use them.
    us_annual_rate: Decimal = Decimal(0)
    us_fixed_fee: Decimal = Decimal(0)
    db_path: str = "chasekit.db"

    @classmethod
    def from_env(cls) -> Settings:
        settings = cls()
        name = os.environ.get("CHASEKIT_BUSINESS_NAME")
        if name:
            settings.business_name = name
        return settings
