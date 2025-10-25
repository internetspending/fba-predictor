"""Pytest configuration and fixtures for testing."""

from collections.abc import AsyncGenerator
from typing import TYPE_CHECKING

import pytest
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from apps.api.app.persistence.tables import Base

if TYPE_CHECKING:
    from fastapi.testclient import TestClient

    from apps.api.app.persistence.tables import Product, User

# Test database URL (in-memory SQLite)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
async def db_engine() -> AsyncEngine:
    """Create async database engine for testing."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine
    await engine.dispose()


@pytest.fixture
async def db_session(db_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """Create async database session for testing."""
    async_session = sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def test_user(db_session: AsyncSession) -> "User":
    """Create a test user."""
    from apps.api.app.persistence.crud import create_user

    return await create_user(db_session, "test@example.com")


@pytest.fixture
async def test_product(db_session: AsyncSession) -> "Product":
    """Create a test product."""
    from apps.api.app.persistence.crud import create_product

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
    from fastapi.testclient import TestClient

    from apps.api.app.main import app

    return TestClient(app)
