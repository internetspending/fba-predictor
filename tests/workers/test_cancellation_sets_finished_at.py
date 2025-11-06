"""Tests for cancellation handling."""

import asyncio
from unittest.mock import patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.persistence.scan_repo import get_scan
from apps.api.app.persistence.tables import Scan
from apps.api.app.workers.pipeline import run_scan

pytestmark = pytest.mark.m5


async def test_cancellation_sets_finished_at(db_session: AsyncSession):
    """Test that cancellation sets finished_at and error='cancelled'."""
    scan = Scan()
    db_session.add(scan)
    await db_session.commit()
    await db_session.refresh(scan)

    # Mock asyncio.gather to raise CancelledError
    with patch("apps.api.app.workers.pipeline.asyncio.gather") as mock_gather:
        mock_gather.side_effect = asyncio.CancelledError("Test cancellation")

        # Run scan - should handle cancellation
        try:
            await run_scan(scan.id)
        except asyncio.CancelledError:
            pass  # Expected

        # Verify scan status is failed with cancellation
        updated = await get_scan(db_session, scan.id)
        assert updated is not None
        assert updated.status == "failed"
        assert updated.error == "cancelled"
        assert updated.finished_at is not None


async def test_cancellation_during_processing(db_session: AsyncSession):
    """Test cancellation during item processing."""
    scan = Scan()
    db_session.add(scan)
    await db_session.commit()
    await db_session.refresh(scan)

    # Mock the gather call to raise CancelledError
    async def mock_gather(*args, **kwargs):
        # Simulate cancellation during processing
        raise asyncio.CancelledError("Processing cancelled")

    with patch("apps.api.app.workers.pipeline.asyncio.gather", side_effect=mock_gather):
        try:
            await run_scan(scan.id)
        except asyncio.CancelledError:
            pass  # Expected

        # Verify status updated
        updated = await get_scan(db_session, scan.id)
        assert updated is not None
        assert updated.finished_at is not None
