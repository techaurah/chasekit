"""Jurisdiction packs: statutory late-payment interest and fixed fees.

Build the pack set for a run with `build_packs(settings)`. Adding a
country means adding one module here plus tests. See
docs/interest-rules.md for the statutes each pack encodes.
"""

from __future__ import annotations

from decimal import Decimal

from ..config import Settings
from .base import InterestResult, JurisdictionPack
from .eu import EUPack
from .uk import UKPack
from .us import USPack

__all__ = [
    "EUPack",
    "InterestResult",
    "JurisdictionPack",
    "UKPack",
    "USPack",
    "build_packs",
]


def build_packs(settings: Settings) -> dict[str, JurisdictionPack]:
    return {
        "UK": UKPack(base_rate=settings.uk_base_rate),
        "EU": EUPack(reference_rate=settings.eu_reference_rate),
        "US": USPack(
            annual_rate=settings.us_annual_rate,
            fixed_fee=settings.us_fixed_fee,
        ),
    }


def get_pack(packs: dict[str, JurisdictionPack], key: str) -> JurisdictionPack:
    pack = packs.get(key.upper())
    if pack is None:
        supported = ", ".join(sorted(packs))
        raise ValueError(f"Unknown jurisdiction '{key}'. Supported packs: {supported}.")
    return pack


# Re-exported for tests that construct packs from raw numbers.
def uk_pack(base_rate: str) -> UKPack:
    return UKPack(base_rate=Decimal(base_rate))


def eu_pack(reference_rate: str) -> EUPack:
    return EUPack(reference_rate=Decimal(reference_rate))
