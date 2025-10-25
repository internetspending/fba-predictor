"""Test CRUD operations for ScanHistory model."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.persistence.crud import (
    create_scan_history,
    delete_scan_history,
    get_product_scan_history,
    get_scan_history,
    get_user_scan_history,
)


@pytest.mark.asyncio
async def test_create_scan_history(db_session: AsyncSession, test_user, test_product):
    """Test creating a new scan history entry."""
    # Await the fixtures to get the actual objects
    user = await test_user
    product = await test_product

    scan_data = {"price": 29.99, "rank": 1000, "reviews": 50, "rating": 4.5}

    scan = await create_scan_history(
        db_session, user_id=user.id, product_id=product.id, results=scan_data, notes="Test scan"
    )

    assert scan.user_id == user.id
    assert scan.product_id == product.id
    assert scan.results == scan_data
    assert scan.notes == "Test scan"
    assert scan.id is not None


@pytest.mark.asyncio
async def test_get_scan_history(db_session: AsyncSession, test_user, test_product):
    """Test getting a scan history entry by ID."""
    user = await test_user
    product = await test_product

    scan_data = {"price": 29.99, "rank": 1000}
    scan = await create_scan_history(
        db_session, user_id=user.id, product_id=product.id, results=scan_data
    )

    retrieved_scan = await get_scan_history(db_session, scan.id)
    assert retrieved_scan is not None
    assert retrieved_scan.id == scan.id


@pytest.mark.asyncio
async def test_get_user_scan_history(db_session: AsyncSession, test_user, test_product):
    """Test getting scan history for a user."""
    user = await test_user
    product = await test_product

    # Create multiple scans
    scan1 = await create_scan_history(
        db_session, user_id=user.id, product_id=product.id, results={"price": 29.99}
    )

    scan2 = await create_scan_history(
        db_session, user_id=user.id, product_id=product.id, results={"price": 31.99}
    )

    EXPECTED_SCAN_COUNT = 2
    scans = await get_user_scan_history(db_session, user.id, limit=10)
    assert len(scans) == EXPECTED_SCAN_COUNT
    assert scans[0].id in [scan1.id, scan2.id]


@pytest.mark.asyncio
async def test_get_product_scan_history(db_session: AsyncSession, test_user, test_product):
    """Test getting scan history for a product."""
    user = await test_user
    product = await test_product

    # Create multiple scans
    scan1 = await create_scan_history(
        db_session, user_id=user.id, product_id=product.id, results={"price": 29.99}
    )

    scan2 = await create_scan_history(
        db_session, user_id=user.id, product_id=product.id, results={"price": 31.99}
    )

    EXPECTED_PRODUCT_SCAN_COUNT = 2
    scans = await get_product_scan_history(db_session, product.id, limit=10)
    assert len(scans) == EXPECTED_PRODUCT_SCAN_COUNT
    assert scans[0].id in [scan1.id, scan2.id]


@pytest.mark.asyncio
async def test_delete_scan_history(db_session: AsyncSession, test_user, test_product):
    """Test deleting a scan history entry."""
    user = await test_user
    product = await test_product

    scan = await create_scan_history(
        db_session, user_id=user.id, product_id=product.id, results={"price": 29.99}
    )

    result = await delete_scan_history(db_session, scan.id)
    assert result is True

    # Verify scan is deleted
    deleted_scan = await get_scan_history(db_session, scan.id)
    assert deleted_scan is None
