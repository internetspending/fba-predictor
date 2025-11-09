"""Scan API endpoints."""

from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.persistence.db import get_db
from apps.api.app.persistence.scan_repo import get_scan
from apps.api.app.persistence.tables import Scan
from apps.api.app.workers.pipeline import run_scan

router = APIRouter()


async def create_scan_internal(db: AsyncSession) -> Scan:
    """Create a new scan in the database."""
    scan = Scan()
    db.add(scan)
    await db.commit()
    await db.refresh(scan)
    return scan


def enqueue_scan(background_tasks: BackgroundTasks, scan_id: UUID) -> None:
    """Enqueue a scan for background processing."""
    background_tasks.add_task(run_scan, scan_id, ruleset=None)


@router.post("/dev/create-scan", tags=["dev"])
async def create_scan_endpoint(db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    """
    Create a new scan (dev endpoint).

    In production, scans would be created via proper upload endpoints.
    """
    scan = await create_scan_internal(db)
    return {"scan_id": str(scan.id), "status": scan.status}


@router.post("/dev/run-scan/{scan_id}", tags=["dev"])
async def run_scan_endpoint(
    scan_id: UUID,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """
    Trigger a scan to run in the background (dev endpoint).

    Args:
        scan_id: Scan UUID
        background_tasks: FastAPI BackgroundTasks
        db: Database session

    Returns:
        Status confirmation
    """
    # Verify scan exists
    scan = await get_scan(db, scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    # Enqueue for background processing
    enqueue_scan(background_tasks, scan_id)

    return {"status": "enqueued", "scan_id": str(scan_id)}


@router.get("/dev/scan/{scan_id}", tags=["dev"])
async def get_scan_endpoint(
    scan_id: UUID, db: AsyncSession = Depends(get_db)
) -> dict[str, str | None]:
    """
    Get scan status (dev endpoint).

    Args:
        scan_id: Scan UUID
        db: Database session

    Returns:
        Scan status information
    """
    scan = await get_scan(db, scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    return {
        "scan_id": str(scan.id),
        "status": scan.status,
        "created_at": scan.created_at.isoformat() if scan.created_at else None,
        "started_at": scan.started_at.isoformat() if scan.started_at else None,
        "finished_at": scan.finished_at.isoformat() if scan.finished_at else None,
        "error": scan.error,
    }
