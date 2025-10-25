"""Test CRUD operations for SavedProduct model."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.persistence.crud import (
    create_product,
    create_saved_product,
    delete_saved_product,
    get_saved_product,
    get_user_saved_products,
)


@pytest.mark.asyncio
async def test_create_saved_product(db_session: AsyncSession, test_user, test_product):
    """Test creating a new saved product entry."""
    user = test_user
    product = test_product

    saved = await create_saved_product(
        db_session, user_id=user.id, product_id=product.id, notes="My favorite product"
    )

    assert saved.user_id == user.id
    assert saved.product_id == product.id
    assert saved.notes == "My favorite product"
    assert saved.id is not None


@pytest.mark.asyncio
async def test_get_saved_product(db_session: AsyncSession, test_user, test_product):
    """Test getting a saved product by ID."""
    user = test_user
    product = test_product

    saved = await create_saved_product(
        db_session, user_id=user.id, product_id=product.id, notes="Test saved product"
    )

    retrieved_saved = await get_saved_product(db_session, saved.id)
    assert retrieved_saved is not None
    assert retrieved_saved.id == saved.id
    assert retrieved_saved.notes == "Test saved product"


@pytest.mark.asyncio
async def test_get_user_saved_products(db_session: AsyncSession, test_user, test_product):
    """Test getting saved products for a user."""
    user = test_user
    product = test_product

    # Create multiple saved products
    saved1 = await create_saved_product(
        db_session, user_id=user.id, product_id=product.id, notes="First saved product"
    )

    # Create another product for the second saved item
    product2 = await create_product(db_session, asin="B08N5WRWNW2", title="Test Product 2")

    saved2 = await create_saved_product(
        db_session, user_id=user.id, product_id=product2.id, notes="Second saved product"
    )

    EXPECTED_SAVED_COUNT = 2
    saved_products = await get_user_saved_products(db_session, user.id, limit=10)
    assert len(saved_products) == EXPECTED_SAVED_COUNT
    assert saved_products[0].id in [saved1.id, saved2.id]


@pytest.mark.asyncio
async def test_delete_saved_product(db_session: AsyncSession, test_user, test_product):
    """Test deleting a saved product."""
    user = test_user
    product = test_product

    saved = await create_saved_product(
        db_session, user_id=user.id, product_id=product.id, notes="Test saved product"
    )

    result = await delete_saved_product(db_session, saved.id)
    assert result is True

    # Verify saved product is deleted
    deleted_saved = await get_saved_product(db_session, saved.id)
    assert deleted_saved is None
