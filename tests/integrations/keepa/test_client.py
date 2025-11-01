"""Tests for KeepaClient."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from apps.api.app.integrations.keepa.client import (
    KeepaAuthError,
    KeepaClient,
    KeepaHTTPError,
    KeepaRateLimitError,
)

pytestmark = pytest.mark.m3


@pytest.fixture
def keepa_client():
    """Create KeepaClient instance for testing."""
    client = KeepaClient(api_key="test_key", base_url="https://api.keepa.com")
    # Mock sleep to be instant
    client._sleep = lambda s: None  # type: ignore[assignment]
    return client


@pytest.fixture
def sample_product_json():
    """Load sample Keepa product JSON."""
    fixture_path = Path(__file__).parent.parent.parent / "fixtures" / "keepa" / "product_basic.json"
    with open(fixture_path) as f:
        return json.load(f)


def test_get_product_success(keepa_client, sample_product_json):
    """Test successful product fetch returns dict."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = sample_product_json

    with patch("httpx.Client") as mock_client_class:
        mock_client = MagicMock()
        mock_client.__enter__ = lambda self: self
        mock_client.__exit__ = lambda *args: None
        mock_client.get.return_value = mock_response
        mock_client_class.return_value = mock_client

        result = keepa_client.get_product("B08N5WRWNW", domain=1)
        assert result == sample_product_json
        assert "products" in result


def test_get_product_rate_limit_error(keepa_client):
    """Test 429 raises KeepaRateLimitError."""
    mock_response = MagicMock()
    mock_response.status_code = 429
    mock_response.text = "Rate limit exceeded"

    with patch("httpx.Client") as mock_client_class:
        mock_client = MagicMock()
        mock_client.__enter__ = lambda self: self
        mock_client.__exit__ = lambda *args: None
        mock_client.get.return_value = mock_response
        mock_client_class.return_value = mock_client

        with pytest.raises(KeepaRateLimitError) as exc_info:
            keepa_client.get_product("B08N5WRWNW")
        assert exc_info.value.status == 429


def test_get_product_auth_error_401(keepa_client):
    """Test 401 raises KeepaAuthError."""
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.text = "Unauthorized"

    with patch("httpx.Client") as mock_client_class:
        mock_client = MagicMock()
        mock_client.__enter__ = lambda self: self
        mock_client.__exit__ = lambda *args: None
        mock_client.get.return_value = mock_response
        mock_client_class.return_value = mock_client

        with pytest.raises(KeepaAuthError) as exc_info:
            keepa_client.get_product("B08N5WRWNW")
        assert exc_info.value.status == 401


def test_get_product_auth_error_403(keepa_client):
    """Test 403 raises KeepaAuthError."""
    mock_response = MagicMock()
    mock_response.status_code = 403
    mock_response.text = "Forbidden"

    with patch("httpx.Client") as mock_client_class:
        mock_client = MagicMock()
        mock_client.__enter__ = lambda self: self
        mock_client.__exit__ = lambda *args: None
        mock_client.get.return_value = mock_response
        mock_client_class.return_value = mock_client

        with pytest.raises(KeepaAuthError) as exc_info:
            keepa_client.get_product("B08N5WRWNW")
        assert exc_info.value.status == 403


def test_get_product_5xx_retries(keepa_client, sample_product_json):
    """Test 5xx retries then succeeds."""
    # Create responses: first two 500, third 200
    responses_list = [
        MagicMock(status_code=500, text="Internal Server Error"),
        MagicMock(status_code=500, text="Internal Server Error"),
        MagicMock(status_code=200, json=MagicMock(return_value=sample_product_json)),
    ]
    call_count = [0]

    def get_side_effect(*args, **kwargs):
        response = responses_list[call_count[0]]
        call_count[0] += 1
        return response

    with patch("httpx.Client") as mock_client_class:
        mock_client = MagicMock()
        mock_client.__enter__ = lambda self: self
        mock_client.__exit__ = lambda *args: None
        mock_client.get.side_effect = get_side_effect
        mock_client_class.return_value = mock_client

        # Should succeed after retries
        result = keepa_client.get_product("B08N5WRWNW")
        assert result == sample_product_json
        assert call_count[0] == 3


def test_get_product_5xx_max_retries(keepa_client):
    """Test 5xx max retries then raises KeepaHTTPError."""
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"

    with patch("httpx.Client") as mock_client_class:
        mock_client = MagicMock()
        mock_client.__enter__ = lambda self: self
        mock_client.__exit__ = lambda *args: None
        mock_client.get.return_value = mock_response
        mock_client_class.return_value = mock_client

        # Should raise after max retries
        with pytest.raises(KeepaHTTPError) as exc_info:
            keepa_client.get_product("B08N5WRWNW")
        assert exc_info.value.status == 500
        assert exc_info.value.status_code == 500  # Alias check


def test_get_product_4xx_http_error(keepa_client):
    """Test other 4xx raises KeepaHTTPError."""
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.text = "Not Found"

    with patch("httpx.Client") as mock_client_class:
        mock_client = MagicMock()
        mock_client.__enter__ = lambda self: self
        mock_client.__exit__ = lambda *args: None
        mock_client.get.return_value = mock_response
        mock_client_class.return_value = mock_client

        with pytest.raises(KeepaHTTPError) as exc_info:
            keepa_client.get_product("B08N5WRWNW")
        assert exc_info.value.status == 404
