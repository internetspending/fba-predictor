"""Test database models and relationships."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.persistence.crud import (
    create_product,
    create_saved_product,
    create_scan_history,
    create_user,
)
from apps.api.app.persistence.tables import Product, SavedProduct, ScanHistory, User


@pytest.mark.m2
@pytest.mark.asyncio
async def test_user_model(db_session: AsyncSession) -> None:
    """Test User model creation and fields."""
    user = await create_user(db_session, "model@example.com")
    assert isinstance(user, User)
    assert user.email == "model@example.com"
    assert user.is_active is True
    assert user.created_at is not None


@pytest.mark.m2
@pytest.mark.asyncio
async def test_product_model(db_session: AsyncSession) -> None:
    """Test Product model creation and fields."""
    product = await create_product(
        db_session,
        asin="B08N5WRWNW",
        title="Model Test Product",
        category="Electronics",
    )
    assert isinstance(product, Product)
    assert product.asin == "B08N5WRWNW"
    assert product.title == "Model Test Product"
    assert product.category == "Electronics"


@pytest.mark.m2
@pytest.mark.asyncio
async def test_scan_history_relationships(
    db_session: AsyncSession, test_user, test_product
) -> None:
    """Test ScanHistory model and relationships."""
    scan = await create_scan_history(
        db_session,
        user_id=test_user.id,
        product_id=test_product.id,
        results={"test": "data"},
    )
    assert isinstance(scan, ScanHistory)
    assert scan.user_id == test_user.id
    assert scan.product_id == test_product.id
    # Test relationship loading
    await db_session.refresh(scan, ["user", "product"])
    assert scan.user.email == test_user.email
    assert scan.product.asin == test_product.asin


@pytest.mark.m2
@pytest.mark.asyncio
async def test_saved_product_relationships(
    db_session: AsyncSession, test_user, test_product
) -> None:
    """Test SavedProduct model and relationships."""
    saved = await create_saved_product(db_session, user_id=test_user.id, product_id=test_product.id)
    assert isinstance(saved, SavedProduct)
    assert saved.user_id == test_user.id
    assert saved.product_id == test_product.id
    # Test relationship loading
    await db_session.refresh(saved, ["user", "product"])
    assert saved.user.email == test_user.email
    assert saved.product.asin == test_product.asin
