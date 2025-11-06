"""Repository functions for scan persistence."""

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.persistence.tables import Scan


async def get_scan(db: AsyncSession, scan_id: UUID) -> Scan | None:
    """Get scan by ID."""
    result = await db.execute(select(Scan).where(Scan.id == scan_id))
    return result.scalar_one_or_none()


async def update_scan_status(
    db: AsyncSession,
    scan_id: UUID,
    status: str,
    *,
    error: str | None = None,
    started_at: datetime | None = None,
    finished_at: datetime | None = None,
) -> None:
    """
    Update scan status and related timestamps within a transaction.

    Only mutates relevant columns; commits after update.
    """
    values: dict[str, Any] = {"status": status}
    if error is not None:
        values["error"] = error
    if started_at is not None:
        values["started_at"] = started_at
    if finished_at is not None:
        values["finished_at"] = finished_at

    await db.execute(update(Scan).where(Scan.id == scan_id).values(**values))
    await db.commit()


async def load_selleramp_rows(db: AsyncSession, scan_id: UUID) -> list[dict[str, Any]]:
    """
    Load raw SellerAmp input rows for a scan.

    In dev, returns sample data for testing.
    In production, this would read from a scan input table or file storage.
    """
    from apps.api.app.core.config import settings

    # Return sample data in non-production environments
    if settings.app_env != "production":
        return [
            {
                "asin": "B001234567",
                "title": "Test Product 1",
                "brand": "TestBrand",
                "buy_cost": "10.00",
                "sell_price": "20.00",
            },
            {
                "asin": "B007654321",
                "title": "Test Product 2",
                "brand": "AnotherBrand",
                "buy_cost": "15.50",
                "sell_price": "30.00",
            },
        ]

    # TODO: Implement actual loading from scan input storage
    return []


async def save_results(db: AsyncSession, scan_id: UUID, items: list[dict[str, Any]]) -> int:
    """
    Save scan results.

    Stub implementation: returns count for dev.
    In production, this would write to a scan_results table.

    Returns:
        Number of items saved
    """
    # TODO: Implement actual result persistence
    return len(items)
