"""Tests for rule predicates."""

from decimal import Decimal

import pytest

from apps.api.app.rules import predicates as P

pytestmark = pytest.mark.m4


def test_min_roi_true():
    """Test min_roi returns True when ROI meets threshold."""
    item = {"roi": Decimal("0.50")}
    assert P.min_roi(item, Decimal("0.30")) is True


def test_min_roi_false():
    """Test min_roi returns False when ROI below threshold."""
    item = {"roi": Decimal("0.20")}
    assert P.min_roi(item, Decimal("0.30")) is False


def test_min_roi_missing_field():
    """Test min_roi returns False when ROI field is missing."""
    item = {}
    assert P.min_roi(item, Decimal("0.30")) is False


def test_min_profit_true():
    """Test min_profit returns True when profit meets threshold."""
    item = {"net_profit": Decimal("10.00")}
    assert P.min_profit(item, Decimal("5.00")) is True


def test_min_profit_false():
    """Test min_profit returns False when profit below threshold."""
    item = {"net_profit": Decimal("3.00")}
    assert P.min_profit(item, Decimal("5.00")) is False


def test_min_profit_missing_field():
    """Test min_profit returns False when net_profit field is missing."""
    item = {}
    assert P.min_profit(item, Decimal("5.00")) is False


def test_max_bsr_true():
    """Test max_bsr returns True when BSR is below threshold."""
    item = {"bsr": 5000}
    assert P.max_bsr(item, 10000) is True


def test_max_bsr_false():
    """Test max_bsr returns False when BSR exceeds threshold."""
    item = {"bsr": 15000}
    assert P.max_bsr(item, 10000) is False


def test_max_bsr_missing_field():
    """Test max_bsr returns False when BSR field is missing."""
    item = {}
    assert P.max_bsr(item, 10000) is False


def test_min_sellers_true():
    """Test min_sellers returns True when seller count meets threshold."""
    item = {"seller_count": 10}
    assert P.min_sellers(item, 5) is True


def test_min_sellers_alt_field():
    """Test min_sellers works with 'sellers' field."""
    item = {"sellers": 8}
    assert P.min_sellers(item, 5) is True


def test_min_sellers_false():
    """Test min_sellers returns False when seller count below threshold."""
    item = {"seller_count": 3}
    assert P.min_sellers(item, 5) is False


def test_brand_allow_true():
    """Test brand_allow returns True when brand is in allowed list."""
    item = {"brand": "TestBrand"}
    assert P.brand_allow(item, ["TestBrand", "OtherBrand"]) is True


def test_brand_allow_case_insensitive():
    """Test brand_allow is case-insensitive."""
    item = {"brand": "testbrand"}
    assert P.brand_allow(item, ["TestBrand", "OtherBrand"]) is True


def test_brand_allow_false():
    """Test brand_allow returns False when brand not in allowed list."""
    item = {"brand": "BlockedBrand"}
    assert P.brand_allow(item, ["TestBrand", "OtherBrand"]) is False


def test_brand_block_true():
    """Test brand_block returns True when brand is NOT in blocked list."""
    item = {"brand": "AllowedBrand"}
    assert P.brand_block(item, ["BlockedBrand", "OtherBlocked"]) is True


def test_brand_block_false():
    """Test brand_block returns False when brand IS in blocked list."""
    item = {"brand": "BlockedBrand"}
    assert P.brand_block(item, ["BlockedBrand", "OtherBlocked"]) is False


def test_brand_block_case_insensitive():
    """Test brand_block is case-insensitive."""
    item = {"brand": "blockedbrand"}
    assert P.brand_block(item, ["BlockedBrand", "OtherBlocked"]) is False


def test_brand_block_no_brand():
    """Test brand_block returns True when brand field is missing."""
    item = {}
    assert P.brand_block(item, ["BlockedBrand"]) is True


def test_exclude_hazmat_true():
    """Test exclude_hazmat returns True when item is not hazmat."""
    item = {"hazmat": False}
    assert P.exclude_hazmat(item) is True


def test_exclude_hazmat_false():
    """Test exclude_hazmat returns False when item is hazmat."""
    item = {"hazmat": True}
    assert P.exclude_hazmat(item) is False


def test_exclude_hazmat_alt_field():
    """Test exclude_hazmat works with 'is_hazmat' field."""
    item = {"is_hazmat": False}
    assert P.exclude_hazmat(item) is True


def test_exclude_hazmat_missing_field():
    """Test exclude_hazmat returns True when hazmat field is missing."""
    item = {}
    assert P.exclude_hazmat(item) is True
