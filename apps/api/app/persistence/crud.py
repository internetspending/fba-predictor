"""CRUD operations for database models."""

from datetime import datetime
from typing import Any

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from apps.api.app.persistence.tables import Product, SavedProduct, ScanHistory, User


# User CRUD operations
async def create_user(db: AsyncSession, email: str) -> User:
    """Create a new user."""
    user = User(email=email)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_user(db: AsyncSession, user_id: int) -> User | None:
    """Get user by ID."""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """Get user by email."""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def update_user(db: AsyncSession, user_id: int, **kwargs: Any) -> User | None:
    """Update user by ID."""
    kwargs["updated_at"] = datetime.utcnow()
    await db.execute(update(User).where(User.id == user_id).values(**kwargs))
    await db.commit()
    return await get_user(db, user_id)


async def delete_user(db: AsyncSession, user_id: int) -> bool:
    """Delete user by ID."""
    result = await db.execute(delete(User).where(User.id == user_id))
    await db.commit()
    return result.rowcount > 0


# Product CRUD operations
async def create_product(
    db: AsyncSession,
    asin: str,
    title: str,
    **kwargs: str | None,
) -> Product:
    """Create a new product."""
    product = Product(asin=asin, title=title, **kwargs)
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product


async def get_product(db: AsyncSession, product_id: int) -> Product | None:
    """Get product by ID."""
    result = await db.execute(select(Product).where(Product.id == product_id))
    return result.scalar_one_or_none()


async def get_product_by_asin(db: AsyncSession, asin: str) -> Product | None:
    """Get product by ASIN."""
    result = await db.execute(select(Product).where(Product.asin == asin))
    return result.scalar_one_or_none()


async def update_product(db: AsyncSession, product_id: int, **kwargs: Any) -> Product | None:
    """Update product by ID."""
    kwargs["updated_at"] = datetime.utcnow()
    await db.execute(update(Product).where(Product.id == product_id).values(**kwargs))
    await db.commit()
    return await get_product(db, product_id)


async def delete_product(db: AsyncSession, product_id: int) -> bool:
    """Delete product by ID."""
    result = await db.execute(delete(Product).where(Product.id == product_id))
    await db.commit()
    return result.rowcount > 0


# Scan History CRUD operations
async def create_scan_history(
    db: AsyncSession,
    user_id: int,
    product_id: int,
    results: dict,
    notes: str | None = None,
) -> ScanHistory:
    """Create a new scan history entry."""
    scan = ScanHistory(user_id=user_id, product_id=product_id, results=results, notes=notes)
    db.add(scan)
    await db.commit()
    await db.refresh(scan)
    return scan


async def get_scan_history(db: AsyncSession, scan_id: int) -> ScanHistory | None:
    """Get scan history by ID."""
    result = await db.execute(
        select(ScanHistory)
        .options(selectinload(ScanHistory.user), selectinload(ScanHistory.product))
        .where(ScanHistory.id == scan_id)
    )
    return result.scalar_one_or_none()


async def get_user_scan_history(
    db: AsyncSession,
    user_id: int,
    limit: int = 10,
    offset: int = 0,
) -> list[ScanHistory]:
    """Get scan history for a user."""
    result = await db.execute(
        select(ScanHistory)
        .options(selectinload(ScanHistory.product))
        .where(ScanHistory.user_id == user_id)
        .order_by(ScanHistory.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(result.scalars().all())


async def get_product_scan_history(
    db: AsyncSession,
    product_id: int,
    limit: int = 10,
    offset: int = 0,
) -> list[ScanHistory]:
    """Get scan history for a product."""
    result = await db.execute(
        select(ScanHistory)
        .options(selectinload(ScanHistory.user))
        .where(ScanHistory.product_id == product_id)
        .order_by(ScanHistory.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(result.scalars().all())


async def delete_scan_history(db: AsyncSession, scan_id: int) -> bool:
    """Delete scan history by ID."""
    result = await db.execute(delete(ScanHistory).where(ScanHistory.id == scan_id))
    await db.commit()
    return result.rowcount > 0


# Saved Product CRUD operations
async def create_saved_product(
    db: AsyncSession,
    user_id: int,
    product_id: int,
    notes: str | None = None,
) -> SavedProduct:
    """Create a new saved product entry."""
    saved = SavedProduct(user_id=user_id, product_id=product_id, notes=notes)
    db.add(saved)
    await db.commit()
    await db.refresh(saved)
    return saved


async def get_saved_product(db: AsyncSession, saved_id: int) -> SavedProduct | None:
    """Get saved product by ID."""
    result = await db.execute(
        select(SavedProduct)
        .options(selectinload(SavedProduct.user), selectinload(SavedProduct.product))
        .where(SavedProduct.id == saved_id)
    )
    return result.scalar_one_or_none()


async def get_user_saved_products(
    db: AsyncSession,
    user_id: int,
    limit: int = 10,
    offset: int = 0,
) -> list[SavedProduct]:
    """Get saved products for a user."""
    result = await db.execute(
        select(SavedProduct)
        .options(selectinload(SavedProduct.product))
        .where(SavedProduct.user_id == user_id)
        .order_by(SavedProduct.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(result.scalars().all())


async def delete_saved_product(db: AsyncSession, saved_id: int) -> bool:
    """Delete saved product by ID."""
    result = await db.execute(delete(SavedProduct).where(SavedProduct.id == saved_id))
    await db.commit()
    return result.rowcount > 0
