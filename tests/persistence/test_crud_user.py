"""Test CRUD operations for User model."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.persistence.crud import (
    create_user,
    delete_user,
    get_user,
    get_user_by_email,
    update_user,
)


@pytest.mark.asyncio
async def test_create_user(db_session: AsyncSession):
    """Test creating a new user."""
    user = await create_user(db_session, "test@example.com")
    assert user.email == "test@example.com"
    assert user.is_active is True
    assert user.id is not None


@pytest.mark.asyncio
async def test_get_user(db_session: AsyncSession):
    """Test getting a user by ID."""
    user = await create_user(db_session, "test@example.com")
    retrieved_user = await get_user(db_session, user.id)
    assert retrieved_user is not None
    assert retrieved_user.email == "test@example.com"


@pytest.mark.asyncio
async def test_get_user_by_email(db_session: AsyncSession):
    """Test getting a user by email."""
    user = await create_user(db_session, "test@example.com")
    retrieved_user = await get_user_by_email(db_session, "test@example.com")
    assert retrieved_user is not None
    assert retrieved_user.id == user.id


@pytest.mark.asyncio
async def test_update_user(db_session: AsyncSession):
    """Test updating a user."""
    user = await create_user(db_session, "test@example.com")
    updated_user = await update_user(db_session, user.id, is_active=False)
    assert updated_user is not None
    assert updated_user.is_active is False
    assert updated_user.email == "test@example.com"


@pytest.mark.asyncio
async def test_delete_user(db_session: AsyncSession):
    """Test deleting a user."""
    user = await create_user(db_session, "test@example.com")
    result = await delete_user(db_session, user.id)
    assert result is True

    # Verify user is deleted
    deleted_user = await get_user(db_session, user.id)
    assert deleted_user is None
