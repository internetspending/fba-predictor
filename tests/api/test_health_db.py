"""Test health check endpoints with database."""

import pytest
from httpx import AsyncClient

from apps.api.app.main import app


@pytest.mark.m2
@pytest.mark.asyncio
async def test_health_basic() -> None:
    """Test basic health endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/v1/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok", "service": "FBA Profit Predictor"}


@pytest.mark.m2
@pytest.mark.asyncio
async def test_health_db_endpoint() -> None:
    """Test database health check endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/v1/health/db")
        # May return 200 if DB available, or 503 if not - both are valid responses
        assert response.status_code in [200, 503]
        data = response.json()
        assert "status" in data
        assert "service" in data


@pytest.mark.m2
@pytest.mark.asyncio
async def test_health_full_endpoint() -> None:
    """Test full health check endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/v1/health/full")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "checks" in data
        assert "database" in data["checks"]
        assert "redis" in data["checks"]
