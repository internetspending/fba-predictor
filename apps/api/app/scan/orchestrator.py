"""Scan orchestrator for batching and chunking."""

import json
from typing import Any

from apps.api.app.scan.queue import ScanQueue


def chunk(items: list[dict[str, Any]], size: int) -> list[list[dict[str, Any]]]:
    """
    Split items into chunks of specified size.

    Args:
        items: List of items to chunk
        size: Chunk size

    Returns:
        List of item chunks
    """
    return [items[i : i + size] for i in range(0, len(items), size)]


def submit_batch(
    queue: ScanQueue,
    items: list[dict[str, Any]],
    seller_id: str | None,
    *,
    chunk_size: int = 25,
) -> list[str]:
    """
    Submit a batch of items as chunked jobs.

    Args:
        queue: ScanQueue instance
        items: List of items to process
        seller_id: Optional seller ID
        chunk_size: Size of each chunk

    Returns:
        List of job IDs
    """
    jids: list[str] = []
    for part in chunk(items, chunk_size):
        payload = {"seller_id": seller_id, "items": part, "attempt": 0}
        jids.append(queue.enqueue(payload))
    return jids


def fetch_results(queue: ScanQueue, job_id: str) -> dict[str, Any]:
    """
    Fetch results for a completed job.

    Args:
        queue: ScanQueue instance
        job_id: Job ID

    Returns:
        Dict with 'results' and 'counters' keys
    """
    raw = queue.r.get(queue._k(f"job:{job_id}:results"))
    if not raw:
        return {"results": [], "counters": {}}
    if isinstance(raw, bytes | bytearray):
        raw = raw.decode()
    return json.loads(raw)
