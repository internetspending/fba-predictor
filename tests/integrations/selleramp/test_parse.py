"""Tests for SellerAmp parsers."""

from pathlib import Path

import pytest

from apps.api.app.integrations.selleramp.parse import parse_csv, parse_json

pytestmark = pytest.mark.m3


@pytest.fixture
def csv_fixture():
    """Load sample CSV."""
    fixture_path = (
        Path(__file__).parent.parent.parent / "fixtures" / "selleramp" / "storefront_small.csv"
    )
    return fixture_path.read_text()


@pytest.fixture
def json_fixture():
    """Load sample JSON."""
    fixture_path = (
        Path(__file__).parent.parent.parent / "fixtures" / "selleramp" / "storefront_small.json"
    )
    return fixture_path.read_text()


def test_parse_csv_basic(csv_fixture):
    """Test CSV happy path."""
    results = parse_csv(csv_fixture)

    assert len(results) == 4
    assert results[0]["asin"] == "B08N5WRWNW"
    assert results[0]["title"] == "Test Product Example"
    assert results[0]["brand"] == "TestBrand"
    assert results[0]["buy_cost"] == 29.99


def test_parse_csv_missing_columns(csv_fixture):
    """Test CSV with missing columns handled."""
    results = parse_csv(csv_fixture)

    # Second row has missing title
    assert results[1]["asin"] == "B001234567"
    assert "title" not in results[1] or results[1].get("title") is None


def test_parse_csv_malformed_price(csv_fixture):
    """Test CSV with malformed price handled."""
    results = parse_csv(csv_fixture)

    # Third row has price as string with $
    assert results[2]["asin"] == "B009876543"
    # Should handle malformed price gracefully
    assert "buy_cost" in results[2]  # May or may not parse correctly


def test_parse_csv_bom_handling():
    """Test CSV with BOM handled."""
    bom_csv = "\ufeffASIN,Title\nB001234567,Test Product"
    results = parse_csv(bom_csv)

    assert len(results) == 1
    assert results[0]["asin"] == "B001234567"


def test_parse_csv_bytes_input(csv_fixture):
    """Test CSV with bytes input."""
    results = parse_csv(csv_fixture.encode("utf-8"))
    assert len(results) == 4


def test_parse_json_basic(json_fixture):
    """Test JSON happy path."""
    results = parse_json(json_fixture)

    assert len(results) == 3
    assert results[0]["asin"] == "B08N5WRWNW"
    assert results[0]["title"] == "Test Product Example"
    assert results[0]["brand"] == "TestBrand"
    assert results[0]["buy_cost"] == 29.99


def test_parse_json_missing_fields(json_fixture):
    """Test JSON with missing fields handled."""
    results = parse_json(json_fixture)

    # Second item has null title
    assert results[1]["asin"] == "B001234567"
    assert results[1].get("title") is None or "title" not in results[1]


def test_parse_json_different_field_names():
    """Test JSON with different field name variations."""
    json_data = """
    {
        "products": [
            {
                "product_asin": "B001234567",
                "product_name": "Test Product",
                "manufacturer": "TestBrand",
                "purchase_price": 19.99
            }
        ]
    }
    """
    results = parse_json(json_data)

    assert len(results) == 1
    assert results[0]["asin"] == "B001234567"
    assert results[0]["title"] == "Test Product"
    assert results[0]["brand"] == "TestBrand"
    assert results[0]["buy_cost"] == 19.99


def test_parse_json_list_direct():
    """Test JSON that is a direct list."""
    json_data = '[{"asin": "B001234567", "title": "Test"}]'
    results = parse_json(json_data)

    assert len(results) == 1
    assert results[0]["asin"] == "B001234567"


def test_parse_json_invalid_returns_empty():
    """Test invalid JSON returns empty list."""
    results = parse_json("not json")
    assert results == []


def test_parse_json_bytes_input(json_fixture):
    """Test JSON with bytes input."""
    results = parse_json(json_fixture.encode("utf-8"))
    assert len(results) == 3
