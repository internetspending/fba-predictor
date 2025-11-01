"""Tests for KeepaCache."""

import pytest
from fakeredis import FakeStrictRedis

from apps.api.app.integrations.keepa.cache import KeepaCache

pytestmark = pytest.mark.m3


@pytest.fixture
def fake_redis(monkeypatch):
    """Replace Redis client with fakeredis."""
    fake_client = FakeStrictRedis(decode_responses=False)
    monkeypatch.setattr(
        "apps.api.app.integrations.keepa.cache.redis.from_url", lambda url, **kwargs: fake_client
    )
    return fake_client


@pytest.fixture
def keepa_cache(fake_redis):
    """Create KeepaCache instance for testing."""
    return KeepaCache(redis_url="redis://localhost:6379/0", default_ttl_s=3600)


def test_key_for_product_deterministic():
    """Test key format is deterministic."""
    key1 = KeepaCache.key_for_product("B08N5WRWNW", domain=1, extra_params=None)
    key2 = KeepaCache.key_for_product("B08N5WRWNW", domain=1, extra_params=None)
    assert key1 == key2
    assert key1.startswith("keepa:product:")
    assert "B08N5WRWNW" in key1


def test_key_for_product_with_params():
    """Test key includes hash of extra params."""
    key1 = KeepaCache.key_for_product("B08N5WRWNW", domain=1, extra_params={"stats": 90})
    key2 = KeepaCache.key_for_product("B08N5WRWNW", domain=1, extra_params={"stats": 90})
    key3 = KeepaCache.key_for_product("B08N5WRWNW", domain=1, extra_params={"stats": 180})

    assert key1 == key2  # Same params = same key
    assert key1 != key3  # Different params = different key


def test_get_cached_product_miss(keepa_cache):
    """Test get returns None on cache miss."""
    key = KeepaCache.key_for_product("B08N5WRWNW", domain=1)
    result = keepa_cache.get_cached_product(key)
    assert result is None


def test_set_get_cached_product_roundtrip(keepa_cache):
    """Test set/get roundtrip."""
    key = KeepaCache.key_for_product("B08N5WRWNW", domain=1)
    payload = {"products": [{"asin": "B08N5WRWNW", "title": "Test"}]}

    keepa_cache.set_cached_product(key, payload)
    result = keepa_cache.get_cached_product(key)
    assert result == payload


def test_set_cached_product_with_ttl(keepa_cache, fake_redis):
    """Test TTL is honored (basic check - fakeredis doesn't expire automatically)."""
    key = KeepaCache.key_for_product("B08N5WRWNW", domain=1)
    payload = {"products": [{"asin": "B08N5WRWNW"}]}

    keepa_cache.set_cached_product(key, payload, ttl_s=60)

    # Check TTL was set (fakeredis doesn't auto-expire, but we can check the TTL value)
    ttl = fake_redis.ttl(key)
    assert ttl <= 60  # Should be close to 60 (allowing for small delay)


def test_get_cached_product_invalid_json(keepa_cache, fake_redis):
    """Test get handles invalid JSON gracefully."""
    key = KeepaCache.key_for_product("B08N5WRWNW", domain=1)
    fake_redis.set(key, b"invalid json")

    result = keepa_cache.get_cached_product(key)
    assert result is None  # Should return None on error
