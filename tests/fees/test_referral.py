"""Tests for referral fee calculation."""

from decimal import Decimal

import pytest

from apps.api.app.fees.interfaces import FeeInputs
from apps.api.app.fees.referral import compute_referral_fee

pytestmark = pytest.mark.m4


def test_referral_fee_electronics():
    """Test referral fee for Electronics category (15% rate)."""
    inp = FeeInputs(
        category="Electronics",
        sell_price=Decimal("29.99"),
        buy_cost=Decimal("15.00"),
    )

    fee = compute_referral_fee(inp)
    expected = Decimal("29.99") * Decimal("0.15")
    assert fee == expected.quantize(Decimal("0.01"))
    assert fee == Decimal("4.50")


def test_referral_fee_home_kitchen():
    """Test referral fee for Home & Kitchen category (12% rate)."""
    inp = FeeInputs(
        category="Home & Kitchen",
        sell_price=Decimal("99.99"),
        buy_cost=Decimal("50.00"),
    )

    fee = compute_referral_fee(inp)
    expected = Decimal("99.99") * Decimal("0.12")
    assert fee == expected.quantize(Decimal("0.01"))
    assert fee == Decimal("12.00")


def test_referral_fee_unknown_category():
    """Test referral fee for unknown category falls back to default (15%)."""
    inp = FeeInputs(
        category="Unknown Category",
        sell_price=Decimal("20.00"),
        buy_cost=Decimal("10.00"),
    )

    fee = compute_referral_fee(inp)
    expected = Decimal("20.00") * Decimal("0.15")
    assert fee == expected.quantize(Decimal("0.01"))
    assert fee == Decimal("3.00")


def test_referral_fee_rounding():
    """Test referral fee rounds to 2 decimal places."""
    inp = FeeInputs(
        category="Electronics",
        sell_price=Decimal("33.33"),
        buy_cost=Decimal("15.00"),
    )

    fee = compute_referral_fee(inp)
    # 33.33 * 0.15 = 4.9995 -> should round to 5.00
    assert fee == Decimal("5.00")
