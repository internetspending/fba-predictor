"""Tests for pipeline failure handling."""

from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.persistence.scan_repo import get_scan
from apps.api.app.persistence.tables import Scan
from apps.api.app.workers.pipeline import run_scan

pytestmark = pytest.mark.m5


async def test_pipeline_failure_sets_failed_status(db_session: AsyncSession):
    """Test that pipeline failure sets scan status to failed."""
    scan = Scan()
    db_session.add(scan)
    await db_session.commit()
    await db_session.refresh(scan)

    # Mock load_selleramp_rows to raise an exception
    with patch(
        "apps.api.app.workers.pipeline.load_selleramp_rows",
        new_callable=AsyncMock,
    ) as mock_load:
        mock_load.side_effect = Exception("Test error: failed to load rows")

        # Run scan (should fail)
        try:
            await run_scan(scan.id)
        except Exception:
            pass  # Expected to raise

        # Refresh from DB
        updated = await get_scan(db_session, scan.id)
        assert updated is not None
        assert updated.status == "failed"
        assert updated.error is not None
        assert "Test error" in updated.error or "Exception" in updated.error
