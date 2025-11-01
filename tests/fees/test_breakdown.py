"""Tests for complete fee breakdown calculation."""

from decimal import Decimal
from unittest.mock import patch

import pytest

from apps.api.app.fees.calc import compute_breakdown
from apps.api.app.fees.interfaces import Dimensions, FeeInputs

pytestmark = pytest.mark.m4


def test_compute_breakdown_basic():
    """Test complete fee breakdown calculation."""
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

    with patch("apps.api.app.fees.placement.is_placement_enabled", return_value=False):
        breakdown = compute_breakdown(inp)

        # Referral: 29.99 * 0.15 = 4.50
        assert breakdown.referral_fee == Decimal("4.50")
        # FBA: 3.22 (standard)
        assert breakdown.fba_fee == Decimal("3.22")
        # Placement: 0.00 (disabled)
        assert breakdown.placement_fee == Decimal("0.00")
        # Total: 4.50 + 3.22 + 0.00 = 7.72
        assert breakdown.total_fees == Decimal("7.72")
        # Net: 29.99 - 7.72 - 15.00 = 7.27
        assert breakdown.net_profit == Decimal("7.27")
        # ROI: 7.27 / 15.00 = 0.4847...
        assert breakdown.roi.quantize(Decimal("0.0001")) == Decimal("0.4847")


def test_compute_breakdown_with_placement():
    """Test fee breakdown with placement fee enabled."""
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

    with patch("apps.api.app.fees.placement.is_placement_enabled", return_value=True):
        breakdown = compute_breakdown(inp)

        assert breakdown.placement_fee == Decimal("0.50")
        # Total: 4.50 + 3.22 + 0.50 = 8.22
        assert breakdown.total_fees == Decimal("8.22")
        # Net: 29.99 - 8.22 - 15.00 = 6.77
        assert breakdown.net_profit == Decimal("6.77")


def test_compute_breakdown_zero_buy_cost():
    """Test ROI is 0 when buy_cost is 0."""
    inp = FeeInputs(
        category="Electronics",
        sell_price=Decimal("29.99"),
        buy_cost=Decimal("0.00"),
        dimensions=None,
    )

    with patch("apps.api.app.fees.placement.is_placement_enabled", return_value=False):
        breakdown = compute_breakdown(inp)

        assert breakdown.roi == Decimal("0")


def test_compute_breakdown_rounding():
    """Test all fees are rounded to 2 decimal places, ROI to 4."""
    inp = FeeInputs(
        category="Electronics",
        sell_price=Decimal("33.33"),
        buy_cost=Decimal("20.00"),
        dimensions=None,
    )

    with patch("apps.api.app.fees.placement.is_placement_enabled", return_value=False):
        breakdown = compute_breakdown(inp)

        # All currency fields quantized to 0.01
        assert breakdown.referral_fee.quantize(Decimal("0.01")) == breakdown.referral_fee
        assert breakdown.fba_fee.quantize(Decimal("0.01")) == breakdown.fba_fee
        assert breakdown.total_fees.quantize(Decimal("0.01")) == breakdown.total_fees
        assert breakdown.net_profit.quantize(Decimal("0.01")) == breakdown.net_profit
        # ROI quantized to 0.0001
        assert breakdown.roi.quantize(Decimal("0.0001")) == breakdown.roi
