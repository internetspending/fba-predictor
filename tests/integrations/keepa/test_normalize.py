"""Tests for Keepa normalize function."""

import json
from pathlib import Path
from typing import Any

import pytest

from apps.api.app.integrations.keepa.normalize import normalize_product

pytestmark = pytest.mark.m3


@pytest.fixture
def sample_keepa_json():
    """Load sample Keepa product JSON."""
    fixture_path = Path(__file__).parent.parent.parent / "fixtures" / "keepa" / "product_basic.json"
    with open(fixture_path) as f:
        return json.load(f)


def test_normalize_product_basic(sample_keepa_json):
    """Test typical Keepa sample normalized to expected fields."""
    result = normalize_product(sample_keepa_json)

    assert result["asin"] == "B08N5WRWNW"
    assert result["title"] == "Test Product Example"
    assert result["brand"] == "TestBrand"
    assert result["category"] == "Electronics"
    assert "price_current" in result
    assert "bsr" in result
    assert "dimensions" in result


def test_normalize_product_missing_fields():
    """Test missing/null fields handled gracefully."""
    minimal_json = {
        "products": [
            {
                "asin": "B001234567",
                "title": "Minimal Product",
                # Missing brand, category, price, etc.
            }
        ]
    }

    result = normalize_product(minimal_json)
    assert result["asin"] == "B001234567"
    assert result["title"] == "Minimal Product"
    assert "brand" not in result or result.get("brand") is None
    assert "category" not in result or result.get("category") is None


def test_normalize_product_empty_products():
    """Test empty products array returns minimal result."""
    empty_json: dict[str, Any] = {"products": []}
    result = normalize_product(empty_json)
    assert result.get("asin") == "" or "asin" not in result


def test_normalize_product_null_price():
    """Test null price handled gracefully."""
    json_with_null_price = {
        "products": [
            {
                "asin": "B001234567",
                "title": "No Price Product",
                "csv": [None, None, None],  # No price data
            }
        ]
    }

    result = normalize_product(json_with_null_price)
    assert result["asin"] == "B001234567"
    # price_current should not be in result if no valid price
    assert "price_current" not in result or result.get("price_current") is None
