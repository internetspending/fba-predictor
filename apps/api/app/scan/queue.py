"""Redis-backed scan queue."""

import json
import uuid
from typing import Any


class ScanQueue:
    """
    Thin wrapper over Redis-like list ops.

    Expected Redis API subset: rpush, lpop, setnx, get, set, hset, hget, hgetall
    In tests use fakeredis; in prod pass redis.StrictRedis.
    """

    def __init__(self, client, namespace: str = "scan") -> None:
        """
        Initialize scan queue.

        Args:
            client: Redis-like client (fakeredis.FakeRedis or redis.StrictRedis)
            namespace: Redis key namespace prefix
        """
        self.r = client
        self.ns = namespace

    def _k(self, suffix: str) -> str:
        """Generate namespaced Redis key."""
        return f"{self.ns}:{suffix}"

    def enqueue(self, payload: dict[str, Any], job_id: str | None = None) -> str:
        """
        Enqueue a job with idempotent payload storage.

        Args:
            payload: Job payload dict
            job_id: Optional job ID (generated if None)

        Returns:
            Job ID string
        """
        jid = job_id or str(uuid.uuid4())
        # idempotency: stash payload if absent
        self.r.setnx(self._k(f"job:{jid}:payload"), json.dumps(payload))
        self.r.rpush(self._k("queue"), jid)
        self.r.hset(self._k("state"), jid, "QUEUED")
        return jid

    def dequeue(self) -> str | None:
        """
        Dequeue a job ID from the queue.

        Returns:
            Job ID string or None if queue is empty
        """
        jid = self.r.lpop(self._k("queue"))
        if jid is None:
            return None
        return jid.decode() if isinstance(jid, bytes | bytearray) else jid

    def load_payload(self, job_id: str) -> dict[str, Any]:
        """
        Load job payload by job ID.

        Args:
            job_id: Job ID

        Returns:
            Payload dict (empty dict if not found)
        """
        raw = self.r.get(self._k(f"job:{job_id}:payload"))
        if raw is None:
            return {}
        if isinstance(raw, bytes | bytearray):
            raw = raw.decode()
        return json.loads(raw)

    def set_state(self, job_id: str, state: str) -> None:
        """
        Set job state.

        Args:
            job_id: Job ID
            state: State string
        """
        self.r.hset(self._k("state"), job_id, state)

    def get_state(self, job_id: str) -> str | None:
        """
        Get job state.

        Args:
            job_id: Job ID

        Returns:
            State string or None if not found
        """
        val = self.r.hget(self._k("state"), job_id)
        if val is None:
            return None
        return val.decode() if isinstance(val, bytes | bytearray) else val

    def dlq(self, job_id: str, reason: str) -> None:
        """
        Move job to dead-letter queue.

        Args:
            job_id: Job ID
            reason: DLQ reason string
        """
        self.r.rpush(self._k("dlq"), job_id)
        self.r.hset(self._k("dlq_reason"), job_id, reason)
        self.set_state(job_id, "DLQ")
