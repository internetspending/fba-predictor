"""Regression tests for dimensions weight/weight_kg support."""

from decimal import Decimal

import pytest

from apps.api.app.fees.calc import compute_breakdown
from apps.api.app.fees.interfaces import Dimensions, FeeInputs

pytestmark = pytest.mark.m5


def _mk(d: dict) -> Dimensions:
    """Helper to coerce legacy and new payloads similarly to pipeline."""
    w = d.get("weight_kg", d.get("weight"))
    return Dimensions(
        length_cm=Decimal(d.get("length_cm", "0")),
        width_cm=Decimal(d.get("width_cm", "0")),
        height_cm=Decimal(d.get("height_cm", "0")),
        weight_kg=Decimal(w) if w is not None else None,
    )


def test_dimensions_accepts_weight_or_weight_kg():
    """Test that both weight_kg (new) and weight (legacy) produce same results."""
    dims_new = _mk({"length_cm": "10", "width_cm": "5", "height_cm": "2", "weight_kg": "0.3"})
    dims_legacy = _mk({"length_cm": "10", "width_cm": "5", "height_cm": "2", "weight": "0.3"})

    fb1 = compute_breakdown(
        FeeInputs(
            category="Test", sell_price=Decimal("25"), buy_cost=Decimal("10"), dimensions=dims_new
        )
    )
    fb2 = compute_breakdown(
        FeeInputs(
            category="Test",
            sell_price=Decimal("25"),
            buy_cost=Decimal("10"),
            dimensions=dims_legacy,
        )
    )

    assert fb1.total_fees == fb2.total_fees
    assert fb1.net_profit == fb2.net_profit
    assert fb1.roi == fb2.roi


def test_dimensions_prefers_weight_kg_over_weight():
    """Test that weight_kg takes precedence if both are present."""
    dims_both = _mk(
        {"length_cm": "10", "width_cm": "5", "height_cm": "2", "weight": "0.3", "weight_kg": "0.5"}
    )

    # Should use weight_kg (0.5) not weight (0.3)
    assert dims_both.weight_kg == Decimal("0.5")
