"""Token bucket rate limiter."""

import time


class TokenBucket:
    """Token bucket rate limiter implementation."""

    def __init__(
        self, rate_per_sec: float, capacity: int, initial_time: float | None = None
    ) -> None:
        """
        Initialize token bucket.

        Args:
            rate_per_sec: Rate at which tokens are added per second
            capacity: Maximum number of tokens (burst capacity)
            initial_time: Initial timestamp (for testing). If None, uses time.monotonic()
        """
        self.rate = rate_per_sec
        self.capacity = capacity
        self.tokens = float(capacity)
        self.ts = initial_time if initial_time is not None else time.monotonic()

    def allow(self, now: float | None = None) -> bool:
        """
        Check if request is allowed and consume a token if so.

        Args:
            now: Current time (monotonic). If None, uses time.monotonic()

        Returns:
            True if allowed (token consumed), False otherwise
        """
        t = now if now is not None else time.monotonic()
        elapsed = t - self.ts
        self.ts = t
        self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
        if self.tokens >= 1.0:
            self.tokens -= 1.0
            return True
        return False


def can_process(buckets: dict[str, TokenBucket], key: str) -> bool:
    """
    Check if processing is allowed for given bucket key.

    Args:
        buckets: Dictionary of bucket name -> TokenBucket
        key: Bucket key to check

    Returns:
        True if allowed, False otherwise
    """
    if key not in buckets:
        return True  # No limit if bucket doesn't exist
    return buckets[key].allow()
