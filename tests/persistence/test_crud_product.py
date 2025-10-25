"""Test CRUD operations for Product model."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.persistence.crud import (
    create_product,
    delete_product,
    get_product,
    get_product_by_asin,
    update_product,
)


@pytest.mark.asyncio
async def test_create_product(db_session: AsyncSession):
    """Test creating a new product."""
    product = await create_product(
        db_session,
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


@pytest.mark.asyncio
async def test_get_product(db_session: AsyncSession):
    """Test getting a product by ID."""
    product = await create_product(db_session, asin="B08N5WRWNW", title="Test Product")
    retrieved_product = await get_product(db_session, product.id)
    assert retrieved_product is not None
    assert retrieved_product.asin == "B08N5WRWNW"


@pytest.mark.asyncio
async def test_get_product_by_asin(db_session: AsyncSession):
    """Test getting a product by ASIN."""
    product = await create_product(db_session, asin="B08N5WRWNW", title="Test Product")
    retrieved_product = await get_product_by_asin(db_session, "B08N5WRWNW")
    assert retrieved_product is not None
    assert retrieved_product.id == product.id


@pytest.mark.asyncio
async def test_update_product(db_session: AsyncSession):
    """Test updating a product."""
    product = await create_product(db_session, asin="B08N5WRWNW", title="Test Product")
    updated_product = await update_product(
        db_session, product.id, title="Updated Product", brand="NewBrand"
    )
    assert updated_product is not None
    assert updated_product.title == "Updated Product"
    assert updated_product.brand == "NewBrand"


@pytest.mark.asyncio
async def test_delete_product(db_session: AsyncSession):
    """Test deleting a product."""
    product = await create_product(db_session, asin="B08N5WRWNW", title="Test Product")
    result = await delete_product(db_session, product.id)
    assert result is True

    # Verify product is deleted
    deleted_product = await get_product(db_session, product.id)
    assert deleted_product is None
