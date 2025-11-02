"""Tests for rate limiter."""

import pytest

from apps.api.app.scan.rate_limit import TokenBucket, can_process

pytestmark = pytest.mark.m5


def test_token_bucket_initial_allow():
    """Test token bucket allows requests when tokens available."""
    bucket = TokenBucket(rate_per_sec=2.0, capacity=2)
    assert bucket.allow() is True
    assert bucket.allow() is True


def test_token_bucket_depletes():
    """Test token bucket denies when tokens depleted."""
    bucket = TokenBucket(rate_per_sec=2.0, capacity=2)
    assert bucket.allow() is True
    assert bucket.allow() is True
    assert bucket.allow() is False  # No tokens left


def test_token_bucket_refills():
    """Test token bucket refills over time."""
    bucket = TokenBucket(rate_per_sec=2.0, capacity=2, initial_time=0.0)

    # Deplete tokens
    assert bucket.allow(now=0.0) is True
    assert bucket.allow(now=0.0) is True
    assert bucket.allow(now=0.0) is False

    # Wait 0.6 seconds (should refill 1.2 tokens, but capped at capacity=2)
    assert bucket.allow(now=0.6) is True  # Should have 1.2 tokens


def test_token_bucket_burst_capacity():
    """Test token bucket respects capacity limit."""
    bucket = TokenBucket(rate_per_sec=10.0, capacity=2, initial_time=0.0)

    # Deplete
    assert bucket.allow(now=0.0) is True
    assert bucket.allow(now=0.0) is True

    # Wait long time (10 seconds = 100 tokens refill), but capped at capacity=2
    assert bucket.allow(now=10.0) is True
    assert bucket.allow(now=10.0) is True
    assert bucket.allow(now=10.0) is False  # Still only 2 tokens max


def test_can_process_with_bucket():
    """Test can_process helper function."""
    buckets = {
        "seller1": TokenBucket(rate_per_sec=1.0, capacity=1),
        "global": TokenBucket(rate_per_sec=2.0, capacity=2),
    }

    assert can_process(buckets, "seller1") is True
    assert can_process(buckets, "seller1") is False  # Depleted

    assert can_process(buckets, "global") is True
    assert can_process(buckets, "global") is True


def test_can_process_missing_key():
    """Test can_process returns True for missing bucket key."""
    buckets: dict[str, TokenBucket] = {}
    assert can_process(buckets, "nonexistent") is True
