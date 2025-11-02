"""Scan worker with retry and DLQ logic."""

import json
import time
from collections.abc import Callable
from typing import Any

from apps.api.app.scan.backoff import exp_backoff
from apps.api.app.scan.errors import PermanentError, RetryableError
from apps.api.app.scan.queue import ScanQueue
from apps.api.app.scan.states import JobState

# Processor signature: process(items) -> (results, counters)
Processor = Callable[[list[dict[str, Any]]], tuple[list[dict[str, Any]], dict[str, int]]]


class Worker:
    """Scan worker with retry policy and DLQ handling."""

    def __init__(
        self,
        queue: ScanQueue,
        processor: Processor,
        max_attempts: int = 3,
        backoff_base_s: float = 0.5,
        sleep_fn: Callable[[float], None] = time.sleep,
    ) -> None:
        """
        Initialize worker.

        Args:
            queue: ScanQueue instance
            processor: Function that processes items -> (results, counters)
            max_attempts: Maximum retry attempts
            backoff_base_s: Base delay for exponential backoff
            sleep_fn: Sleep function (injectable for tests)
        """
        self.queue = queue
        self.processor = processor
        self.max_attempts = max_attempts
        self.backoff_base_s = backoff_base_s
        self.sleep = sleep_fn

    def run_once(self) -> bool:
        """
        Run one job from the queue.

        Returns:
            True if a job was processed, False if queue was empty
        """
        jid = self.queue.dequeue()
        if not jid:
            return False

        payload = self.queue.load_payload(jid)
        items: list[dict[str, Any]] = payload.get("items", [])
        attempt = int(payload.get("attempt", 0))
        self.queue.set_state(jid, JobState.RUNNING.value)

        for delay in exp_backoff(self.backoff_base_s, self.max_attempts):
            if delay:
                self.queue.set_state(jid, JobState.RETRYING.value)
                self.sleep(delay)

            try:
                results, counters = self.processor(items)

                # store results
                self.queue.set_state(jid, JobState.SUCCEEDED.value)
                self._store_results(jid, results, counters)
                return True

            except PermanentError as e:
                self.queue.set_state(jid, JobState.FAILED.value)
                self.queue.dlq(jid, f"permanent:{e}")
                return True

            except RetryableError as e:
                attempt += 1
                if attempt >= self.max_attempts:
                    self.queue.set_state(jid, JobState.DLQ.value)
                    self.queue.dlq(jid, f"retry_exhausted:{e}")
                    return True
                # loop continues and retries
                payload["attempt"] = attempt

        # safety
        self.queue.set_state(jid, JobState.DLQ.value)
        self.queue.dlq(jid, "exhausted_without_raise")
        return True

    def _store_results(
        self, job_id: str, results: list[dict[str, Any]], counters: dict[str, int]
    ) -> None:
        """
        Store job results in Redis.

        Args:
            job_id: Job ID
            results: Result rows
            counters: Counters dict
        """
        data = {"results": results, "counters": counters}
        # keep in Redis for now
        self.queue.r.set(self.queue._k(f"job:{job_id}:results"), json.dumps(data))
