"""Tests for pipeline status transitions."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.persistence.scan_repo import get_scan, update_scan_status
from apps.api.app.persistence.tables import Scan
from apps.api.app.workers.pipeline import normalize_row

pytestmark = pytest.mark.m5


async def test_scan_status_pending_to_running(db_session: AsyncSession):
    """Test scan status transitions from pending to running."""
    scan = Scan()
    db_session.add(scan)
    await db_session.commit()
    await db_session.refresh(scan)

    assert scan.status == "pending"

    await update_scan_status(db_session, scan.id, "running")

    # Refresh from DB
    updated = await get_scan(db_session, scan.id)
    assert updated is not None
    assert updated.status == "running"


async def test_scan_status_running_to_done(db_session: AsyncSession):
    """Test scan status transitions from running to done."""
    scan = Scan()
    db_session.add(scan)
    await db_session.commit()
    await db_session.refresh(scan)

    await update_scan_status(db_session, scan.id, "running")
    await update_scan_status(db_session, scan.id, "done")

    updated = await get_scan(db_session, scan.id)
    assert updated is not None
    assert updated.status == "done"


async def test_scan_status_running_to_failed(db_session: AsyncSession):
    """Test scan status transitions from running to failed."""
    scan = Scan()
    db_session.add(scan)
    await db_session.commit()
    await db_session.refresh(scan)

    await update_scan_status(db_session, scan.id, "running")
    await update_scan_status(db_session, scan.id, "failed", error="Test error message")

    updated = await get_scan(db_session, scan.id)
    assert updated is not None
    assert updated.status == "failed"
    assert updated.error == "Test error message"


def test_normalize_row():
    """Test normalize_row function."""
    row = {
        "asin": "B001234567",
        "title": "Test Product",
        "brand": "TestBrand",
        "buy_cost": "10.00",
        "sell_price": "20.00",
    }

    normalized = normalize_row(row)

    assert normalized["asin"] == "B001234567"
    assert normalized["title"] == "Test Product"
    assert normalized["brand"] == "TestBrand"
    assert normalized["buy_cost"] is not None


def test_normalize_row_missing_fields():
    """Test normalize_row handles missing fields gracefully."""
    row = {"asin": "B001234567"}

    normalized = normalize_row(row)

    assert normalized["asin"] == "B001234567"
    assert normalized["title"] == ""
    assert normalized["brand"] is None
