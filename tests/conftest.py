"""Pytest configuration and fixtures for testing."""

from collections.abc import AsyncGenerator
from typing import TYPE_CHECKING

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from apps.api.app.main import app
from apps.api.app.persistence.crud import create_product, create_user
from apps.api.app.persistence.tables import Base

if TYPE_CHECKING:
    from apps.api.app.persistence.tables import Product, User

# Test database URL (in-memory SQLite)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


# Store engine at module level for test session
_test_engine: AsyncEngine | None = None


@pytest.fixture(scope="function")
def db_engine() -> AsyncEngine:
    """Create async database engine for testing."""
    global _test_engine
    if _test_engine is None:
        _test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
        # Create tables synchronously via run_async
        import asyncio

        async def create_tables():
            async with _test_engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

        asyncio.run(create_tables())

    yield _test_engine
    # Cleanup handled at end of test session


@pytest.fixture
def db_session_factory(db_engine: AsyncEngine):
    """Return a factory function to create database sessions."""
    async_session = sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)

    async def _get_session() -> AsyncGenerator[AsyncSession, None]:
        async with async_session() as session:
            async with session.begin():
                yield session
                await session.rollback()

    return _get_session


@pytest.fixture
async def test_user(db_session: AsyncSession) -> "User":
    """Create a test user."""
    return await create_user(db_session, "test@example.com")


@pytest.fixture
async def test_product(db_session: AsyncSession) -> "Product":
    """Create a test product."""
    return await create_product(
        db_session,
        asin="B08N5WRWNW",
        title="Test Product",
        category="Electronics",
        brand="TestBrand",
    )


@pytest.fixture
def client() -> "TestClient":
    """Create a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture
async def async_client() -> AsyncGenerator:
    """Create an async test client for the FastAPI application."""

    from httpx import AsyncClient

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
