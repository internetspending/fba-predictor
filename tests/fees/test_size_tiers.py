"""Tests for size tier estimation."""

from decimal import Decimal

import pytest

from apps.api.app.fees.interfaces import Dimensions
from apps.api.app.fees.size_tiers import estimate_size_tier

pytestmark = pytest.mark.m4


def test_size_tier_standard():
    """Test standard size tier for small dimensions."""
    dim = Dimensions(
        length_cm=Decimal("30"),
        width_cm=Decimal("20"),
        height_cm=Decimal("15"),
        weight_kg=Decimal("0.5"),
    )

    assert estimate_size_tier(dim) == "standard"


def test_size_tier_oversize_length():
    """Test oversize tier when length exceeds threshold."""
    dim = Dimensions(
        length_cm=Decimal("50"),  # > 45cm threshold
        width_cm=Decimal("20"),
        height_cm=Decimal("15"),
        weight_kg=Decimal("0.5"),
    )

    assert estimate_size_tier(dim) == "oversize"


def test_size_tier_oversize_weight():
    """Test oversize tier when weight exceeds threshold."""
    dim = Dimensions(
        length_cm=Decimal("30"),
        width_cm=Decimal("20"),
        height_cm=Decimal("15"),
        weight_kg=Decimal("2.0"),  # > 1.8kg threshold
    )

    assert estimate_size_tier(dim) == "oversize"


def test_size_tier_oversize_width():
    """Test oversize tier when width exceeds threshold."""
    dim = Dimensions(
        length_cm=Decimal("30"),
        width_cm=Decimal("50"),  # > 45cm threshold
        height_cm=Decimal("15"),
        weight_kg=Decimal("0.5"),
    )

    assert estimate_size_tier(dim) == "oversize"


def test_size_tier_oversize_height():
    """Test oversize tier when height exceeds threshold."""
    dim = Dimensions(
        length_cm=Decimal("30"),
        width_cm=Decimal("20"),
        height_cm=Decimal("40"),  # > 35cm threshold
        weight_kg=Decimal("0.5"),
    )

    assert estimate_size_tier(dim) == "oversize"


def test_size_tier_no_dimensions():
    """Test size tier returns standard when dimensions are None."""
    assert estimate_size_tier(None) == "standard"


def test_size_tier_boundary_length():
    """Test size tier boundary case for length (exactly at threshold)."""
    dim = Dimensions(
        length_cm=Decimal("45"),  # Exactly at threshold
        width_cm=Decimal("20"),
        height_cm=Decimal("15"),
        weight_kg=Decimal("0.5"),
    )

    assert estimate_size_tier(dim) == "standard"  # Should be standard (<= not <)


def test_size_tier_boundary_weight():
    """Test size tier boundary case for weight (exactly at threshold)."""
    dim = Dimensions(
        length_cm=Decimal("30"),
        width_cm=Decimal("20"),
        height_cm=Decimal("15"),
        weight_kg=Decimal("1.8"),  # Exactly at threshold
    )

    assert estimate_size_tier(dim) == "standard"  # Should be standard (<= not <)
