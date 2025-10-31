"""Test CRUD operations for database models."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.persistence.crud import (
    create_product,
    create_saved_product,
    create_scan_history,
    create_user,
    delete_product,
    delete_saved_product,
    delete_user,
    get_product,
    get_product_by_asin,
    get_saved_product,
    get_scan_history,
    get_user,
    get_user_by_email,
    get_user_saved_products,
    update_product,
    update_user,
)


@pytest.mark.m2
async def test_create_user(db_session_factory) -> None:
    """Test creating a user."""
    async for session in db_session_factory():
        user = await create_user(session, "test@example.com")
        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.is_active is True
        break


@pytest.mark.m2
@pytest.mark.asyncio
async def test_get_user(db_session: AsyncSession) -> None:
    """Test getting a user by ID."""
    user = await create_user(db_session, "gettest@example.com")
    retrieved = await get_user(db_session, user.id)
    assert retrieved is not None
    assert retrieved.email == "gettest@example.com"


@pytest.mark.m2
@pytest.mark.asyncio
async def test_get_user_by_email(db_session: AsyncSession) -> None:
    """Test getting a user by email."""
    email = "emailtest@example.com"
    user = await create_user(db_session, email)
    retrieved = await get_user_by_email(db_session, email)
    assert retrieved is not None
    assert retrieved.id == user.id


@pytest.mark.m2
@pytest.mark.asyncio
async def test_update_user(db_session: AsyncSession) -> None:
    """Test updating a user."""
    user = await create_user(db_session, "updatetest@example.com")
    updated = await update_user(db_session, user.id, is_active=False)
    assert updated is not None
    assert updated.is_active is False


@pytest.mark.m2
@pytest.mark.asyncio
async def test_delete_user(db_session: AsyncSession) -> None:
    """Test deleting a user."""
    user = await create_user(db_session, "deletetest@example.com")
    result = await delete_user(db_session, user.id)
    assert result is True
    retrieved = await get_user(db_session, user.id)
    assert retrieved is None


@pytest.mark.m2
@pytest.mark.asyncio
async def test_create_product(db_session: AsyncSession) -> None:
    """Test creating a product."""
    product = await create_product(
        db_session,
        asin="B08N5WRWNW",
        title="Test Product",
        category="Electronics",
        brand="TestBrand",
    )
    assert product.id is not None
    assert product.asin == "B08N5WRWNW"
    assert product.title == "Test Product"


@pytest.mark.m2
@pytest.mark.asyncio
async def test_get_product_by_asin(db_session: AsyncSession) -> None:
    """Test getting a product by ASIN."""
    asin = "B08N5WRWNW"
    await create_product(db_session, asin=asin, title="Test Product")
    retrieved = await get_product_by_asin(db_session, asin)
    assert retrieved is not None
    assert retrieved.asin == asin


@pytest.mark.m2
@pytest.mark.asyncio
async def test_update_product(db_session: AsyncSession) -> None:
    """Test updating a product."""
    product = await create_product(db_session, asin="B08N5WRWNW", title="Original Title")
    updated = await update_product(db_session, product.id, title="Updated Title")
    assert updated is not None
    assert updated.title == "Updated Title"


@pytest.mark.m2
@pytest.mark.asyncio
async def test_delete_product(db_session: AsyncSession) -> None:
    """Test deleting a product."""
    product = await create_product(db_session, asin="B08N5WRWNW", title="Test Product")
    result = await delete_product(db_session, product.id)
    assert result is True
    retrieved = await get_product(db_session, product.id)
    assert retrieved is None


@pytest.mark.m2
@pytest.mark.asyncio
async def test_create_scan_history(db_session: AsyncSession, test_user, test_product) -> None:
    """Test creating scan history."""
    scan = await create_scan_history(
        db_session,
        user_id=test_user.id,
        product_id=test_product.id,
        results={"roi": 25.5, "net_profit": 100.0},
        notes="Test scan",
    )
    assert scan.id is not None
    assert scan.results["roi"] == 25.5


@pytest.mark.m2
@pytest.mark.asyncio
async def test_get_scan_history(db_session: AsyncSession, test_user, test_product) -> None:
    """Test getting scan history."""
    scan = await create_scan_history(
        db_session,
        user_id=test_user.id,
        product_id=test_product.id,
        results={"roi": 30.0},
    )
    retrieved = await get_scan_history(db_session, scan.id)
    assert retrieved is not None
    assert retrieved.results["roi"] == 30.0


@pytest.mark.m2
@pytest.mark.asyncio
async def test_create_saved_product(db_session: AsyncSession, test_user, test_product) -> None:
    """Test creating a saved product."""
    saved = await create_saved_product(
        db_session, user_id=test_user.id, product_id=test_product.id, notes="Favorite"
    )
    assert saved.id is not None
    assert saved.notes == "Favorite"


@pytest.mark.m2
@pytest.mark.asyncio
async def test_get_user_saved_products(db_session: AsyncSession, test_user, test_product) -> None:
    """Test getting saved products for a user."""
    await create_saved_product(db_session, user_id=test_user.id, product_id=test_product.id)
    saved_products = await get_user_saved_products(db_session, test_user.id)
    assert len(saved_products) == 1
    assert saved_products[0].product_id == test_product.id


@pytest.mark.m2
@pytest.mark.asyncio
async def test_delete_saved_product(db_session: AsyncSession, test_user, test_product) -> None:
    """Test deleting a saved product."""
    saved = await create_saved_product(db_session, user_id=test_user.id, product_id=test_product.id)
    result = await delete_saved_product(db_session, saved.id)
    assert result is True
    retrieved = await get_saved_product(db_session, saved.id)
    assert retrieved is None
