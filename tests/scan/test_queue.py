"""Tests for scan queue."""

from typing import Any

import pytest
from fakeredis import FakeStrictRedis

from apps.api.app.scan.queue import ScanQueue

pytestmark = pytest.mark.m5


@pytest.fixture
def fake_redis():
    """Create fake Redis client for testing."""
    return FakeStrictRedis(decode_responses=False)


@pytest.fixture
def queue(fake_redis):
    """Create ScanQueue instance for testing."""
    return ScanQueue(fake_redis, namespace="scan")


def test_enqueue_returns_job_id(queue):
    """Test enqueue returns job_id."""
    payload: dict[str, Any] = {"seller_id": "seller1", "items": [{"asin": "B001"}]}
    jid = queue.enqueue(payload)
    assert isinstance(jid, str)
    assert len(jid) > 0


def test_enqueue_stores_payload(queue):
    """Test enqueue stores payload."""
    payload: dict[str, Any] = {"seller_id": "seller1", "items": [{"asin": "B001"}]}
    jid = queue.enqueue(payload)
    loaded = queue.load_payload(jid)
    assert loaded == payload


def test_enqueue_sets_state_queued(queue):
    """Test enqueue sets state to QUEUED."""
    payload = {"items": []}
    jid = queue.enqueue(payload)
    state = queue.get_state(jid)
    assert state == "QUEUED"


def test_dequeue_returns_job_id(queue):
    """Test dequeue returns job_id when available."""
    payload = {"items": []}
    jid = queue.enqueue(payload)
    dequeued = queue.dequeue()
    assert dequeued == jid


def test_dequeue_returns_none_when_empty(queue):
    """Test dequeue returns None when queue is empty."""
    result = queue.dequeue()
    assert result is None


def test_load_payload_returns_empty_when_missing(queue):
    """Test load_payload returns empty dict when job not found."""
    result = queue.load_payload("nonexistent")
    assert result == {}


def test_set_state_updates_state(queue):
    """Test set_state updates job state."""
    jid = queue.enqueue({"items": []})
    queue.set_state(jid, "RUNNING")
    assert queue.get_state(jid) == "RUNNING"


def test_dlq_moves_to_dlq(queue):
    """Test dlq moves job to dead-letter queue."""
    payload = {"items": []}
    jid = queue.enqueue(payload)
    queue.dlq(jid, "test reason")

    state = queue.get_state(jid)
    assert state == "DLQ"

    # Check DLQ list contains job_id
    dlq_list = queue.r.lrange(queue._k("dlq"), 0, -1)
    assert jid.encode() in dlq_list or jid in [
        x.decode() if isinstance(x, bytes) else x for x in dlq_list
    ]

    # Check reason is stored
    reason = queue.r.hget(queue._k("dlq_reason"), jid)
    if isinstance(reason, bytes):
        reason = reason.decode()
    assert reason == "test reason"
