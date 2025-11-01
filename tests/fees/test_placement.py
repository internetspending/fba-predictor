"""Tests for placement fee calculation."""

from decimal import Decimal
from unittest.mock import patch

import pytest

from apps.api.app.fees.interfaces import FeeInputs
from apps.api.app.fees.placement import compute_placement_fee

pytestmark = pytest.mark.m4


def test_placement_fee_disabled():
    """Test placement fee returns 0 when feature is disabled."""
    with patch("apps.api.app.fees.placement.is_placement_enabled", return_value=False):
        inp = FeeInputs(
            category="Electronics",
            sell_price=Decimal("29.99"),
            buy_cost=Decimal("15.00"),
        )

        fee = compute_placement_fee(inp)
        assert fee == Decimal("0.00")


def test_placement_fee_enabled():
    """Test placement fee returns default fee when feature is enabled."""
    with patch("apps.api.app.fees.placement.is_placement_enabled", return_value=True):
        inp = FeeInputs(
            category="Electronics",
            sell_price=Decimal("29.99"),
            buy_cost=Decimal("15.00"),
        )

        fee = compute_placement_fee(inp)
        assert fee == Decimal("0.50")  # Default placement fee


def test_placement_fee_rounding():
    """Test placement fee is rounded to 2 decimal places."""
    with patch("apps.api.app.fees.placement.is_placement_enabled", return_value=True):
        inp = FeeInputs(
            category="Electronics",
            sell_price=Decimal("29.99"),
            buy_cost=Decimal("15.00"),
        )

        fee = compute_placement_fee(inp)
        assert fee.quantize(Decimal("0.01")) == fee
