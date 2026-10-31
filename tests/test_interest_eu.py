"""EU pack tests. Every number here is hand-checkable.

Rate used: reference rate 2.15% + 8 percentage points = 10.15%
(Directive 2011/7/EU). Interest = principal * 10.15% * days / 365.
"""

from decimal import Decimal

from chasekit.interest.eu import EUPack
from chasekit.interest.us import USPack


def pack() -> EUPack:
    return EUPack(reference_rate=Decimal("2.15"))


def test_rate_is_reference_plus_eight():
    assert pack().annual_rate_percent() == Decimal("10.15")


def test_interest_sixty_days_on_2000():
    # 2000 * 0.1015 * 60 / 365 = 12180 / 365 = 33.3698... -> 33.37
    result = pack().calculate(Decimal(2000), 60)
    assert result.interest == Decimal("33.37")


def test_total_for_2000_at_60_days():
    # Fixed compensation is the EUR 40 statutory minimum.
    result = pack().calculate(Decimal(2000), 60)
    assert result.fixed_fee == Decimal("40.00")
    assert result.total_due == Decimal("2073.37")


def test_minimum_fee_applies_to_small_invoices():
    result = pack().calculate(Decimal(25), 5)
    assert result.fixed_fee == Decimal("40.00")


def test_invoice_1003_from_examples():
    # 5000 * 0.1015 * 29 / 365 = 14717.5 / 365 = 40.3220... -> 40.32
    result = pack().calculate(Decimal(5000), 29)
    assert result.interest == Decimal("40.32")
    assert result.total_due == Decimal("5080.32")


def test_basis_names_the_directive():
    assert "2011/7/EU" in pack().basis()


def test_us_default_is_zero_and_honest():
    result = USPack().calculate(Decimal(1500), 11)
    assert result.interest == Decimal("0.00")
    assert result.fixed_fee == Decimal("0.00")
    assert result.total_due == Decimal(1500)


def test_us_configured_rate():
    # 1000 * 0.18 * 30 / 365 = 5400 / 365 = 14.7945... -> 14.79
    us = USPack(annual_rate=Decimal(18), fixed_fee=Decimal(25))
    result = us.calculate(Decimal(1000), 30)
    assert result.interest == Decimal("14.79")
    assert result.total_due == Decimal("1039.79")
