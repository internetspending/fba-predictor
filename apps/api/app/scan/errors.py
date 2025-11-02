"""Scan pipeline error types."""


class RetryableError(Exception):
    """Transient errors: network hiccup, rate limit, 5xx."""

    pass


class PermanentError(Exception):
    """Non-retryable: bad data shape, unsupported category, etc."""

    pass
