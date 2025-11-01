"""Keepa API client with retry logic and error handling."""

import time
from typing import TYPE_CHECKING, Any

import httpx

if TYPE_CHECKING:
    from apps.api.app.integrations.keepa.cache import KeepaCache


class KeepaError(Exception):
    """Base exception for Keepa API errors."""

    pass


class KeepaHTTPError(KeepaError):
    """Raised when Keepa API returns a non-2xx status."""

    def __init__(self, status: int, message: str = "", *, response_text: str | None = None):
        super().__init__(f"[{status}] {message}")
        self.status = status
        self.status_code = status  # Alias for backwards compatibility
        self.response_text = response_text


class KeepaRateLimitError(KeepaHTTPError):
    """Raised when Keepa API returns 429 (rate limit)."""

    pass


class KeepaAuthError(KeepaHTTPError):
    """Raised when Keepa API returns 401/403 (authentication/authorization)."""

    pass


class KeepaClient:
    """HTTP client for Keepa API with retry and error handling."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = "https://api.keepa.com",
        timeout_s: float = 15.0,
        max_retries: int = 3,
        backoff_base_s: float = 0.5,
    ) -> None:
        """
        Initialize Keepa client.

        Args:
            api_key: Keepa API key (if None, must be provided per request)
            base_url: Base URL for Keepa API
            timeout_s: HTTP request timeout in seconds
            max_retries: Maximum number of retry attempts
            backoff_base_s: Base wait time for exponential backoff
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout_s = timeout_s
        self.max_retries = max_retries
        self.backoff_base_s = backoff_base_s

    def _sleep(self, seconds: float) -> None:
        """Sleep for specified seconds (injectable for tests)."""
        time.sleep(seconds)

    def get_product(
        self, asin: str, *, domain: int = 1, extra_params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Fetch product JSON for a single ASIN.

        Args:
            asin: Amazon ASIN
            domain: Keepa domain ID (1 = US)
            extra_params: Additional query parameters

        Returns:
            Product data as dict from Keepa API

        Raises:
            KeepaRateLimitError: On 429 responses
            KeepaAuthError: On 401/403 responses
            KeepaHTTPError: On other non-2xx responses or after max retries
        """
        params: dict[str, Any] = {"asin": asin, "domain": domain}
        if self.api_key:
            params["key"] = self.api_key
        if extra_params:
            params.update(extra_params)

        attempt = 0
        last_err: Exception | None = None
        backoff = self.backoff_base_s

        while attempt <= self.max_retries:
            try:
                with httpx.Client(timeout=self.timeout_s) as client:
                    resp = client.get(f"{self.base_url}/product", params=params)

                if resp.status_code == 200:
                    return resp.json()

                if resp.status_code == 429:
                    raise KeepaRateLimitError(429, "rate limited", response_text=resp.text)

                if resp.status_code in (401, 403):
                    raise KeepaAuthError(resp.status_code, "auth error", response_text=resp.text)

                # 5xx and other non-2xx that are retryable:
                if 500 <= resp.status_code < 600 and attempt < self.max_retries:
                    attempt += 1
                    self._sleep(backoff)
                    backoff *= 2
                    continue

                # Non-retryable final error:
                raise KeepaHTTPError(resp.status_code, "http error", response_text=resp.text)

            except (httpx.ConnectError, httpx.ReadTimeout) as e:
                last_err = e
                if attempt < self.max_retries:
                    attempt += 1
                    self._sleep(backoff)
                    backoff *= 2
                    continue
                raise KeepaHTTPError(599, "network error") from e
            except (KeepaRateLimitError, KeepaAuthError, KeepaHTTPError):
                # Don't retry these errors
                raise

        # Should never reach here; loop exits via return/raise
        raise KeepaHTTPError(599, "unexpected error") from last_err


def get_product_enriched(
    asin: str,
    *,
    client: KeepaClient,
    cache: "KeepaCache",
    domain: int = 1,
) -> dict[str, Any]:
    """
    Get product with caching: check cache first, then call Keepa if needed.

    Args:
        asin: Amazon ASIN
        client: KeepaClient instance
        cache: KeepaCache instance
        domain: Keepa domain ID (1 = US)

    Returns:
        Product data from cache or Keepa API
    """
    key = cache.key_for_product(asin, domain, extra_params=None)
    cached = cache.get_cached_product(key)
    if cached is not None:
        return cached

    data = client.get_product(asin, domain=domain)
    cache.set_cached_product(key, data)
    return data
