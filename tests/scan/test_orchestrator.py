"""Tests for scan orchestrator."""

import json
from pathlib import Path

import pytest
from fakeredis import FakeStrictRedis

from apps.api.app.scan.orchestrator import chunk, fetch_results, submit_batch
from apps.api.app.scan.queue import ScanQueue
from apps.api.app.scan.worker import Worker

pytestmark = pytest.mark.m5


@pytest.fixture
def queue():
    """Create ScanQueue with fake Redis."""
    return ScanQueue(FakeStrictRedis(decode_responses=False))


@pytest.fixture
def sample_items():
    """Load sample items from fixture."""
    fixture_path = Path(__file__).parent.parent / "fixtures" / "scan" / "storefront_small.json"
    with open(fixture_path) as f:
        return json.load(f)


def fake_processor(items):
    """Fake processor for testing."""
    results = [
        {"asin": it.get("asin", ""), "kept": it.get("price", 0) > 10, "reason": "ok"}
        for it in items
    ]
    counters = {"parsed": len(items), "kept": sum(1 for r in results if r["kept"]), "skipped": 0}
    return results, counters


def test_chunk_splits_correctly():
    """Test chunk splits items into correct sizes."""
    items = [{"asin": f"B{i:03d}"} for i in range(12)]
    chunks = chunk(items, 5)
    assert len(chunks) == 3
    assert len(chunks[0]) == 5
    assert len(chunks[1]) == 5
    assert len(chunks[2]) == 2


def test_chunk_empty_list():
    """Test chunk handles empty list."""
    chunks = chunk([], 5)
    assert chunks == []


def test_submit_batch_enqueues_chunks(queue, sample_items):
    """Test submit_batch enqueues chunked jobs."""
    jids = submit_batch(queue, sample_items, seller_id="seller1", chunk_size=5)
    assert len(jids) >= 2  # Should create multiple jobs for 8-12 items


def test_submit_batch_stores_payloads(queue, sample_items):
    """Test submit_batch stores correct payloads."""
    jids = submit_batch(queue, sample_items, seller_id="seller1", chunk_size=5)

    for jid in jids:
        payload = queue.load_payload(jid)
        assert "seller_id" in payload
        assert payload["seller_id"] == "seller1"
        assert "items" in payload
        assert "attempt" in payload
        assert payload["attempt"] == 0


def test_orchestrator_workflow(queue, sample_items):
    """Test full orchestrator workflow: submit -> process -> fetch."""
    # Submit batch
    jids = submit_batch(queue, sample_items, seller_id="seller1", chunk_size=5)
    assert len(jids) > 0

    # Process jobs
    worker = Worker(queue, fake_processor, sleep_fn=lambda s: None)
    processed = 0
    while worker.run_once():
        processed += 1

    assert processed == len(jids)

    # Fetch and verify results
    total_parsed = 0
    total_kept = 0
    for jid in jids:
        results_data = fetch_results(queue, jid)
        assert "results" in results_data
        assert "counters" in results_data
        total_parsed += results_data["counters"].get("parsed", 0)
        total_kept += results_data["counters"].get("kept", 0)

    assert total_parsed == len(sample_items)
    assert total_kept >= 0
