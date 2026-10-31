"""UK pack tests. Every number here is hand-checkable.

Rate used: Bank of England base rate 4.00% + 8% statutory uplift = 12%.
Interest = principal * 12% * days / 365.
"""

from decimal import Decimal

from chasekit.interest.uk import UKPack


def pack() -> UKPack:
    return UKPack(base_rate=Decimal("4.00"))


def test_rate_is_base_plus_eight():
    assert pack().annual_rate_percent() == Decimal("12.00")


def test_interest_thirty_days_on_1000():
    # 1000 * 0.12 * 30 / 365 = 3600 / 365 = 9.8630... -> 9.86
    result = pack().calculate(Decimal(1000), 30)
    assert result.interest == Decimal("9.86")


def test_total_for_1000_at_30_days():
    # Fee band for exactly 1000 is 70. Total = 1000 + 9.86 + 70.
    result = pack().calculate(Decimal(1000), 30)
    assert result.fixed_fee == Decimal("70.00")
    assert result.total_due == Decimal("1079.86")


def test_interest_ten_days_on_500():
    # 500 * 0.12 * 10 / 365 = 600 / 365 = 1.6438... -> 1.64
    result = pack().calculate(Decimal(500), 10)
    assert result.interest == Decimal("1.64")
    assert result.total_due == Decimal("541.64")


def test_fixed_fee_bands():
    p = pack()
    assert p.fixed_fee_for(Decimal("0.01")) == Decimal("40.00")
    assert p.fixed_fee_for(Decimal("999.99")) == Decimal("40.00")
    assert p.fixed_fee_for(Decimal(1000)) == Decimal("70.00")
    assert p.fixed_fee_for(Decimal("9999.99")) == Decimal("70.00")
    assert p.fixed_fee_for(Decimal(10000)) == Decimal("100.00")
    assert p.fixed_fee_for(Decimal(250000)) == Decimal("100.00")


def test_large_invoice_at_47_days():
    # Matches example INV-1004: 12000 * 0.12 * 47 / 365 = 67680 / 365
    # = 185.4246... -> 185.42; fee 100; total 12285.42.
    result = pack().calculate(Decimal(12000), 47)
    assert result.interest == Decimal("185.42")
    assert result.total_due == Decimal("12285.42")


def test_no_interest_or_fee_when_not_overdue():
    result = pack().calculate(Decimal(1000), 0)
    assert result.interest == Decimal("0.00")
    assert result.fixed_fee == Decimal("0.00")
    assert result.total_due == Decimal(1000)


def test_basis_names_the_act():
    assert "Late Payment of Commercial Debts" in pack().basis()
