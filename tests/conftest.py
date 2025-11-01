"""Pytest configuration and fixtures for testing."""

from collections.abc import AsyncGenerator
from typing import TYPE_CHECKING

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import Session, sessionmaker

from apps.api.app.main import app
from apps.api.app.persistence.crud import create_product, create_user
from apps.api.app.persistence.tables import Base

if TYPE_CHECKING:
    from apps.api.app.persistence.tables import Product, User

# Test database URL (in-memory SQLite)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
TEST_DATABASE_URL_SYNC = "sqlite:///:memory:"


@pytest.fixture(scope="function")
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
        async with session.begin():
            yield session
            await session.rollback()


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


@pytest.fixture(scope="function")
def db_session_sync() -> Session:
    """Create sync database session for testing (used for snapshot persistence)."""
    engine = create_engine(TEST_DATABASE_URL_SYNC, echo=False)

    # Create all tables
    Base.metadata.create_all(engine)

    session_local = sessionmaker(bind=engine, expire_on_commit=False)
    session = session_local()

    try:
        yield session
    finally:
        session.rollback()
        session.close()
        engine.dispose()
