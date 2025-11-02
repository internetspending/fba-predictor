"""Exponential backoff helper."""

from collections.abc import Iterator


def exp_backoff(base_s: float, max_attempts: int) -> Iterator[float]:
    """
    Yield 0, base, 2*base, 4*base, ... for max_attempts.

    First 0 avoids sleeping before first try.

    Args:
        base_s: Base delay in seconds
        max_attempts: Maximum number of attempts

    Yields:
        Delay in seconds for each attempt (starts with 0)
    """
    delay = 0.0
    for _attempt in range(max_attempts):
        yield delay
        delay = max(base_s, delay * 2 if delay else base_s)
