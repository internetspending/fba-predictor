"""Simple CRUD tests without complex fixtures."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from apps.api.app.persistence.crud import create_product, create_user, get_product, get_user
from apps.api.app.persistence.tables import Base

# Test database URL (in-memory SQLite)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.mark.asyncio
async def test_user_crud_operations():
    """Test basic user CRUD operations."""
    # Create engine and session
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Test create user
        user = await create_user(session, "test@example.com")
        assert user.email == "test@example.com"
        assert user.is_active is True
        assert user.id is not None

        # Test get user
        retrieved_user = await get_user(session, user.id)
        assert retrieved_user is not None
        assert retrieved_user.email == "test@example.com"

    await engine.dispose()


@pytest.mark.asyncio
async def test_product_crud_operations():
    """Test basic product CRUD operations."""
    # Create engine and session
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Test create product
        product = await create_product(
            session,
            asin="B08N5WRWNW",
            title="Test Product",
            category="Electronics",
            brand="TestBrand",
        )
        assert product.asin == "B08N5WRWNW"
        assert product.title == "Test Product"
        assert product.category == "Electronics"
        assert product.brand == "TestBrand"
        assert product.id is not None

        # Test get product
        retrieved_product = await get_product(session, product.id)
        assert retrieved_product is not None
        assert retrieved_product.asin == "B08N5WRWNW"

    await engine.dispose()
