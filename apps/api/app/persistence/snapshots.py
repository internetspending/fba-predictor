"""Persistence layer for raw Keepa API snapshots."""

from typing import Any

from sqlalchemy.orm import Session

from apps.api.app.persistence.tables import KeepaSnapshot


def persist_keepa_snapshot(
    db: Session, *, asin: str, payload: dict[str, Any], source: str = "keepa"
) -> int:
    """
    Insert raw JSON payload + metadata into keepa_snapshots table.

    Args:
        db: Database session (sync)
        asin: Amazon ASIN
        payload: Raw Keepa API response JSON
        source: Source identifier (default: "keepa")

    Returns:
        Inserted row id (primary key)
    """
    snapshot = KeepaSnapshot(asin=asin, source=source, payload=payload)
    db.add(snapshot)
    db.flush()  # Get PK without full commit (fixture usually rolls back)
    return snapshot.id
