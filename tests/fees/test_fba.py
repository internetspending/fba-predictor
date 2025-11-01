"""Tests for FBA fee calculation."""

from decimal import Decimal

import pytest

from apps.api.app.fees.fba import compute_fba_fee
from apps.api.app.fees.interfaces import Dimensions, FeeInputs

pytestmark = pytest.mark.m4


def test_fba_fee_standard():
    """Test FBA fee for standard size tier."""
    inp = FeeInputs(
        category="Electronics",
        sell_price=Decimal("29.99"),
        buy_cost=Decimal("15.00"),
        dimensions=Dimensions(
            length_cm=Decimal("30"),
            width_cm=Decimal("20"),
            height_cm=Decimal("15"),
            weight_kg=Decimal("0.5"),
        ),
    )

    fee = compute_fba_fee(inp)
    assert fee == Decimal("3.22")  # Standard base fee


def test_fba_fee_oversize():
    """Test FBA fee for oversize tier."""
    inp = FeeInputs(
        category="Electronics",
        sell_price=Decimal("99.99"),
        buy_cost=Decimal("50.00"),
        dimensions=Dimensions(
            length_cm=Decimal("50"),
            width_cm=Decimal("40"),
            height_cm=Decimal("30"),
            weight_kg=Decimal("2.5"),
        ),
    )

    fee = compute_fba_fee(inp)
    assert fee == Decimal("6.10")  # Oversize base fee


def test_fba_fee_no_dimensions():
    """Test FBA fee defaults to standard when dimensions are None."""
    inp = FeeInputs(
        category="Electronics",
        sell_price=Decimal("29.99"),
        buy_cost=Decimal("15.00"),
        dimensions=None,
    )

    fee = compute_fba_fee(inp)
    assert fee == Decimal("3.22")  # Standard base fee


def test_fba_fee_rounding():
    """Test FBA fee is rounded to 2 decimal places."""
    inp = FeeInputs(
        category="Electronics",
        sell_price=Decimal("29.99"),
        buy_cost=Decimal("15.00"),
        dimensions=Dimensions(
            length_cm=Decimal("30"),
            width_cm=Decimal("20"),
            height_cm=Decimal("15"),
            weight_kg=Decimal("0.5"),
        ),
    )

    fee = compute_fba_fee(inp)
    # Should be quantized to 2 decimal places
    assert fee.quantize(Decimal("0.01")) == fee
