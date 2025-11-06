"""Tests for idempotent scan execution."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.persistence.scan_repo import get_scan, update_scan_status
from apps.api.app.persistence.tables import Scan
from apps.api.app.workers.pipeline import run_scan

pytestmark = pytest.mark.m5


async def test_run_scan_twice_is_idempotent(db_session: AsyncSession):
    """Test that running a scan twice returns zeros on second run."""
    # Create scan
    scan = Scan()
    db_session.add(scan)
    await db_session.commit()
    await db_session.refresh(scan)

    # First run - should process
    counts1 = await run_scan(scan.id)

    # Verify first run completed
    updated1 = await get_scan(db_session, scan.id)
    assert updated1 is not None
    assert updated1.status == "done"
    assert counts1.extracted > 0  # Should have processed items

    # Second run - should skip and return zeros
    counts2 = await run_scan(scan.id)

    # Verify second run returned zeros
    assert counts2.extracted == 0
    assert counts2.transformed == 0
    assert counts2.loaded == 0
    assert counts2.skipped == 0
    assert counts2.errors == 0

    # Verify status still done
    updated2 = await get_scan(db_session, scan.id)
    assert updated2 is not None
    assert updated2.status == "done"


async def test_run_scan_skips_running_scan(db_session: AsyncSession):
    """Test that running a scan that's already running is skipped."""
    scan = Scan()
    db_session.add(scan)
    await db_session.commit()
    await db_session.refresh(scan)

    # Set status to running
    await update_scan_status(db_session, scan.id, "running")

    # Try to run - should skip
    counts = await run_scan(scan.id)

    # Should return zeros
    assert counts.extracted == 0
    assert counts.transformed == 0

    # Status should still be running (not changed)
    updated = await get_scan(db_session, scan.id)
    assert updated is not None
    assert updated.status == "running"
