"""Main FastAPI application entry point."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from apps.api.app.api.v1 import health
from apps.api.app.core.config import settings
from apps.api.app.persistence.db import close_db, init_db


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    # Startup
    await init_db()
    yield
    # Shutdown
    await close_db()


# Create FastAPI application
app = FastAPI(
    title="FBA Profit Predictor API",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/v1/health", tags=["health"])

# Include scan router (dev endpoints only in non-production)
if settings.app_env != "production":
    from apps.api.app.api.v1 import scan

    app.include_router(scan.router, prefix="/v1", tags=["scan"])


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {"message": "FBA Profit Predictor API", "version": "1.0.0"}
