"""Health check endpoints for monitoring service status."""

from typing import Any

import redis.asyncio as redis
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.core.config import settings
from apps.api.app.persistence.db import get_db

router = APIRouter()

# Module-level dependency to avoid B008 error
_db_dependency = Depends(get_db)


@router.get("/")
async def health() -> dict[str, str]:
    """Basic health check endpoint."""
    return {"status": "ok", "service": "FBA Profit Predictor"}


@router.get("/db")
async def health_db(db: AsyncSession = _db_dependency) -> dict[str, Any]:
    """Database connectivity health check."""
    try:
        # Test database connection with a simple query
        result = await db.execute(text("SELECT 1 as test"))
        row = result.fetchone()
        if row and row[0] == 1:
            return {
                "status": "ok",
                "service": "database",
                "message": "Database connection successful",
            }
        else:
            raise HTTPException(status_code=503, detail="Database query failed")
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database connection failed: {e!s}") from e


@router.get("/redis")
async def health_redis() -> dict[str, Any]:
    """Redis connectivity health check."""
    try:
        # Test Redis connection
        redis_client = redis.from_url(settings.redis_url)
        await redis_client.ping()
        await redis_client.close()
        return {
            "status": "ok",
            "service": "redis",
            "message": "Redis connection successful",
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Redis connection failed: {e!s}") from e


@router.get("/full")
async def health_full(db: AsyncSession = _db_dependency) -> dict[str, Any]:
    """Comprehensive health check including all services."""
    health_status: dict[str, Any] = {
        "status": "ok",
        "service": "FBA Profit Predictor",
        "checks": {},
    }

    # Check database
    try:
        await db.execute(text("SELECT 1 as test"))
        health_status["checks"]["database"] = {
            "status": "ok",
            "message": "Database connection successful",
        }
    except Exception as e:
        health_status["checks"]["database"] = {
            "status": "error",
            "message": f"Database connection failed: {e!s}",
        }
        health_status["status"] = "degraded"

    # Check Redis
    try:
        redis_client = redis.from_url(settings.redis_url)
        await redis_client.ping()
        await redis_client.close()
        health_status["checks"]["redis"] = {
            "status": "ok",
            "message": "Redis connection successful",
        }
    except Exception as e:
        health_status["checks"]["redis"] = {
            "status": "error",
            "message": f"Redis connection failed: {e!s}",
        }
        health_status["status"] = "degraded"

    return health_status
