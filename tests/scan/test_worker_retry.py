"""Tests for worker retry logic."""

import pytest
from fakeredis import FakeStrictRedis

from apps.api.app.scan.errors import PermanentError, RetryableError
from apps.api.app.scan.queue import ScanQueue
from apps.api.app.scan.states import JobState
from apps.api.app.scan.worker import Worker

pytestmark = pytest.mark.m5


@pytest.fixture
def queue():
    """Create ScanQueue with fake Redis."""
    return ScanQueue(FakeStrictRedis(decode_responses=False))


def fake_processor_ok(items):
    """Fake processor that always succeeds."""
    results = [{"asin": it.get("asin", ""), "kept": True, "reason": "ok"} for it in items]
    counters = {"parsed": len(items), "kept": len(items), "skipped": 0}
    return results, counters


def fake_processor_retry_once_factory():
    """Factory for processor that fails once then succeeds."""
    called = {"n": 0}

    def _proc(items):
        if called["n"] == 0:
            called["n"] += 1
            raise RetryableError("transient")
        return fake_processor_ok(items)

    return _proc


def fake_processor_permanent(items):
    """Fake processor that raises PermanentError."""
    raise PermanentError("bad input")


def fake_processor_always_retry(items):
    """Fake processor that always raises RetryableError."""
    raise RetryableError("always transient")


def test_worker_succeeds_on_ok_processor(queue):
    """Test worker succeeds when processor succeeds."""
    worker = Worker(queue, fake_processor_ok, max_attempts=3, sleep_fn=lambda s: None)
    jid = queue.enqueue({"items": [{"asin": "B001"}]})

    result = worker.run_once()
    assert result is True

    state = queue.get_state(jid)
    assert state == JobState.SUCCEEDED.value

    # Check results stored
    results_data = fetch_results(queue, jid)
    assert "results" in results_data
    assert "counters" in results_data
    assert results_data["counters"]["parsed"] == 1


def test_worker_retries_on_retryable_error(queue):
    """Test worker retries and succeeds after retryable error."""
    worker = Worker(
        queue,
        fake_processor_retry_once_factory(),
        max_attempts=3,
        backoff_base_s=0.1,
        sleep_fn=lambda s: None,
    )
    jid = queue.enqueue({"items": [{"asin": "B001"}]})

    result = worker.run_once()
    assert result is True

    state = queue.get_state(jid)
    assert state == JobState.SUCCEEDED.value


def test_worker_dlq_on_permanent_error(queue):
    """Test worker moves to DLQ on permanent error."""
    worker = Worker(queue, fake_processor_permanent, max_attempts=3, sleep_fn=lambda s: None)
    jid = queue.enqueue({"items": [{"asin": "B001"}]})

    result = worker.run_once()
    assert result is True

    state = queue.get_state(jid)
    # Permanent error sets to FAILED then DLQ is called which sets to DLQ
    assert state == JobState.DLQ.value

    # Check DLQ reason
    dlq_reason = queue.r.hget(queue._k("dlq_reason"), jid)
    if isinstance(dlq_reason, bytes):
        dlq_reason = dlq_reason.decode()
    assert dlq_reason is not None
    assert "permanent" in dlq_reason.lower()


def test_worker_dlq_on_exhausted_retries(queue):
    """Test worker moves to DLQ when retries exhausted."""
    worker = Worker(
        queue,
        fake_processor_always_retry,
        max_attempts=3,
        backoff_base_s=0.1,
        sleep_fn=lambda s: None,
    )
    jid = queue.enqueue({"items": [{"asin": "B001"}]})

    result = worker.run_once()
    assert result is True

    state = queue.get_state(jid)
    assert state == JobState.DLQ.value

    # Check DLQ reason
    dlq_reason = queue.r.hget(queue._k("dlq_reason"), jid)
    if isinstance(dlq_reason, bytes):
        dlq_reason = dlq_reason.decode()
    assert dlq_reason is not None
    assert "retry_exhausted" in dlq_reason.lower() or "exhausted" in dlq_reason.lower()


def test_worker_returns_false_when_queue_empty(queue):
    """Test worker returns False when queue is empty."""
    worker = Worker(queue, fake_processor_ok, sleep_fn=lambda s: None)
    result = worker.run_once()
    assert result is False


def fetch_results(queue, job_id):
    """Helper to fetch results from queue."""
    from apps.api.app.scan.orchestrator import fetch_results

    return fetch_results(queue, job_id)
