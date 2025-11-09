from __future__ import annotations

import logging
from decimal import Decimal

import pytest

from apps.api.app.workers.pipeline import build_dimensions

pytestmark = pytest.mark.m5


@pytest.mark.parametrize(
    "weight_raw, expected",
    [
        ("0", Decimal("0")),
        ("0.25", Decimal("0.25")),
    ],
)
def test_dimensions_uses_weight_kg_when_present(
    weight_raw: str, expected: Decimal, caplog: pytest.LogCaptureFixture
) -> None:
    caplog.set_level(logging.WARNING, logger="apps.api.app.workers.pipeline")

    dims = build_dimensions(
        {
            "length_cm": "10",
            "width_cm": "5",
            "height_cm": "2",
            "weight_kg": weight_raw,
        }
    )

    assert dims is not None
    assert dims.weight_kg == expected
    assert "deprecated_weight_field" not in caplog.text


@pytest.mark.parametrize(
    "weight_raw, expected",
    [
        ("0.1", Decimal("0.1")),
        ("1.05", Decimal("1.05")),
    ],
)
def test_dimensions_accepts_legacy_weight_and_warns(
    weight_raw: str, expected: Decimal, caplog: pytest.LogCaptureFixture
) -> None:
    caplog.set_level(logging.WARNING, logger="apps.api.app.workers.pipeline")

    dims = build_dimensions(
        {
            "length_cm": "5",
            "width_cm": "5",
            "height_cm": "5",
            "weight": weight_raw,
        }
    )

    assert dims is not None
    assert dims.weight_kg == expected

    warnings = [
        record.getMessage() for record in caplog.records if record.levelno == logging.WARNING
    ]
    assert any("deprecated_weight_field" in message for message in warnings)
    assert sum("deprecated_weight_field" in message for message in warnings) == 1


@pytest.mark.parametrize(
    "weight_kg_raw, legacy_raw, expected, expect_warning",
    [
        ("0.2", "0.9", Decimal("0.2"), False),
        ("", "0.9", Decimal("0.9"), True),
    ],
)
def test_dimensions_prefers_weight_kg_over_legacy(
    weight_kg_raw: str,
    legacy_raw: str,
    expected: Decimal,
    expect_warning: bool,
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level(logging.WARNING, logger="apps.api.app.workers.pipeline")

    dims = build_dimensions(
        {
            "length_cm": "3",
            "width_cm": "3",
            "height_cm": "3",
            "weight_kg": weight_kg_raw,
            "weight": legacy_raw,
        }
    )

    assert dims is not None
    assert dims.weight_kg == expected

    warnings = [
        record.getMessage() for record in caplog.records if record.levelno == logging.WARNING
    ]
    has_warning = any("deprecated_weight_field" in message for message in warnings)
    assert has_warning is expect_warning
