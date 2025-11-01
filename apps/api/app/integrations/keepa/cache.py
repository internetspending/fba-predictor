"""Redis cache layer for Keepa API responses."""

import hashlib
import json
from typing import Any

import redis

from apps.api.app.core.config import settings


class KeepaCache:
    """Redis-based cache for Keepa product data."""

    def __init__(self, redis_url: str | None = None, default_ttl_s: int = 86400) -> None:
        """
        Initialize Keepa cache.

        Args:
            redis_url: Redis connection URL (defaults to settings.redis_url)
            default_ttl_s: Default TTL in seconds (default: 86400 = 24 hours)
        """
        self.redis_url = redis_url or settings.redis_url
        self.default_ttl_s = default_ttl_s
        self._client: redis.Redis | None = None

    @property
    def client(self) -> redis.Redis:
        """Get or create Redis client (lazy initialization)."""
        if self._client is None:
            self._client = redis.from_url(self.redis_url, decode_responses=False)
        return self._client

    @staticmethod
    def key_for_product(asin: str, domain: int, extra_params: dict[str, Any] | None = None) -> str:
        """
        Generate deterministic cache key for product.

        Format: 'keepa:product:{domain}:{asin}:{hash_of_params}'

        Args:
            asin: Amazon ASIN
            domain: Keepa domain ID
            extra_params: Additional query parameters (used for key hash)

        Returns:
            Cache key string
        """
        key_parts = ["keepa", "product", str(domain), asin]

        if extra_params:
            # Sort params for deterministic hash
            sorted_params = json.dumps(extra_params, sort_keys=True, separators=(",", ":"))
            param_hash = hashlib.md5(sorted_params.encode()).hexdigest()[:8]
            key_parts.append(param_hash)

        return ":".join(key_parts)

    def get_cached_product(self, key: str) -> dict[str, Any] | None:
        """
        Retrieve cached product data.

        Args:
            key: Cache key from key_for_product()

        Returns:
            Cached product data as dict, or None if not found
        """
        try:
            cached_bytes = self.client.get(key)
            if cached_bytes is None:
                return None
            decoded = cached_bytes.decode("utf-8")
            return json.loads(decoded)
        except (redis.RedisError, json.JSONDecodeError, UnicodeDecodeError):
            # On any error, return None (cache miss)
            return None

    def set_cached_product(
        self, key: str, payload: dict[str, Any], ttl_s: int | None = None
    ) -> None:
        """
        Cache product data.

        Args:
            key: Cache key from key_for_product()
            payload: Product data to cache
            ttl_s: TTL in seconds (defaults to default_ttl_s)
        """
        try:
            ttl = ttl_s if ttl_s is not None else self.default_ttl_s
            serialized = json.dumps(payload).encode("utf-8")
            self.client.setex(key, ttl, serialized)
        except (redis.RedisError, ValueError):
            # Silently fail on cache write errors (non-critical)
            # ValueError can occur if payload is not JSON serializable
            pass
