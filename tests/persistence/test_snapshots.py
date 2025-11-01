"""Tests for Keepa snapshot persistence."""

from typing import Any

import pytest

from apps.api.app.persistence.snapshots import persist_keepa_snapshot
from apps.api.app.persistence.tables import KeepaSnapshot

pytestmark = pytest.mark.m3


def test_persist_keepa_snapshot_inserts_row(db_session_sync):
    """Test persist_keepa_snapshot inserts row and returns id."""
    payload = {"products": [{"asin": "B08N5WRWNW", "title": "Test"}]}

    snapshot_id = persist_keepa_snapshot(
        db_session_sync, asin="B08N5WRWNW", payload=payload, source="keepa"
    )

    assert isinstance(snapshot_id, int)
    assert snapshot_id > 0

    # Verify row exists
    snapshot = db_session_sync.query(KeepaSnapshot).filter(KeepaSnapshot.id == snapshot_id).one()

    assert snapshot.asin == "B08N5WRWNW"
    assert snapshot.source == "keepa"
    assert snapshot.payload == payload


def test_persist_keepa_snapshot_payload_stored(db_session_sync):
    """Test payload stored correctly."""
    payload = {
        "products": [
            {
                "asin": "B001234567",
                "title": "Another Product",
                "csv": [[150000]],
            }
        ]
    }

    snapshot_id = persist_keepa_snapshot(db_session_sync, asin="B001234567", payload=payload)

    snapshot = db_session_sync.query(KeepaSnapshot).filter(KeepaSnapshot.id == snapshot_id).one()

    assert snapshot.payload == payload
    assert "products" in snapshot.payload


def test_persist_keepa_snapshot_created_at_exists(db_session_sync):
    """Test created_at is set automatically."""
    from datetime import datetime

    payload: dict[str, Any] = {"products": []}
    snapshot_id = persist_keepa_snapshot(db_session_sync, asin="B009876543", payload=payload)

    snapshot = db_session_sync.query(KeepaSnapshot).filter(KeepaSnapshot.id == snapshot_id).one()

    assert snapshot.created_at is not None
    assert isinstance(snapshot.created_at, datetime)
