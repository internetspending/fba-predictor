"""Tests for partial success handling (continue-on-error policy)."""

from unittest.mock import patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.persistence.scan_repo import get_scan
from apps.api.app.persistence.tables import Scan
from apps.api.app.workers.pipeline import normalize_row, run_scan

pytestmark = pytest.mark.m5


async def test_pipeline_continues_on_item_error(db_session: AsyncSession):
    """Test that pipeline continues processing even if one item fails."""
    scan = Scan()
    db_session.add(scan)
    await db_session.commit()
    await db_session.refresh(scan)

    # Mock normalize_row to raise for one item
    original_normalize = normalize_row
    call_count = 0

    def mock_normalize_with_error(row: dict) -> dict:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            # First item fails
            raise ValueError("Invalid data in row")
        # Second item succeeds
        return original_normalize(row)

    with patch(
        "apps.api.app.workers.pipeline.normalize_row", side_effect=mock_normalize_with_error
    ):
        counts = await run_scan(scan.id)

        # Should have extracted 2 items
        assert counts.extracted == 2

        # One should have errored, one should have succeeded
        # Since normalize_row error is caught, it becomes an error count
        assert counts.errors == 1
        assert counts.transformed >= 1  # At least one succeeded

        # Status should be done (partial success allowed)
        updated = await get_scan(db_session, scan.id)
        assert updated is not None
        assert updated.status == "done"


def test_normalize_row_handles_missing_asin():
    """Test that normalize_row handles rows without ASIN gracefully."""
    # Row without ASIN should still return dict (but will be filtered later)
    row = {"title": "Test Product", "brand": "TestBrand"}
    result = normalize_row(row)

    assert isinstance(result, dict)
    assert result["asin"] == ""  # Empty string if missing


def test_normalize_row_handles_invalid_data():
    """Test that normalize_row handles invalid data types."""
    # Row with invalid types
    row = {
        "asin": "B001",
        "title": 12345,  # Invalid type
        "buy_cost": "not_a_number",
    }

    # Should not raise, but normalize gracefully
    result = normalize_row(row)
    assert result["asin"] == "B001"
    assert isinstance(result["title"], str)  # Should convert or handle
