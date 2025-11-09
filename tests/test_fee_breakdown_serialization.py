from __future__ import annotations

import json
from decimal import Decimal

import pytest

from apps.api.app.fees.interfaces import FeeBreakdown
from apps.api.app.workers.pipeline import serialize_fee_breakdown

pytestmark = pytest.mark.m5


def test_fee_breakdown_serialization_round_trip() -> None:
    breakdown = FeeBreakdown(
        referral_fee=Decimal("2.55"),
        fba_fee=Decimal("3.10"),
        placement_fee=Decimal("0.45"),
        total_fees=Decimal("6.10"),
        net_profit=Decimal("1.90"),
        roi=Decimal("0.1234"),
    )

    serialized = serialize_fee_breakdown(breakdown)

    expected = {
        "referral_fee": 2.55,
        "fba_fee": 3.1,
        "placement_fee": 0.45,
        "total_fees": 6.1,
        "net_profit": 1.9,
        "roi": 0.1234,
    }

    assert serialized == expected

    round_trip = json.loads(json.dumps(serialized))
    assert round_trip == expected

    # Ensure values are primitives (no Decimals remain)
    assert all(not isinstance(value, Decimal) for value in serialized.values())
