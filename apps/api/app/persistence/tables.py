"""Database table definitions using SQLAlchemy ORM."""

from datetime import datetime

from sqlalchemy import JSON, ForeignKey, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all database models."""

    pass


class User(Base):
    """User model for storing user information."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())

    # Relationships
    scan_history: Mapped[list["ScanHistory"]] = relationship("ScanHistory", back_populates="user")
    saved_products: Mapped[list["SavedProduct"]] = relationship(
        "SavedProduct", back_populates="user"
    )


class Product(Base):
    """Product model for storing Amazon product information."""

    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    asin: Mapped[str] = mapped_column(String(10), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(500))
    category: Mapped[str | None] = mapped_column(String(100))
    brand: Mapped[str | None] = mapped_column(String(100))
    image_url: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())

    # Relationships
    scan_history: Mapped[list["ScanHistory"]] = relationship(
        "ScanHistory", back_populates="product"
    )
    saved_products: Mapped[list["SavedProduct"]] = relationship(
        "SavedProduct", back_populates="product"
    )


class ScanHistory(Base):
    """Scan history model for storing product scan results."""

    __tablename__ = "scan_history"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), index=True)
    results: Mapped[dict] = mapped_column(JSON)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=func.now())

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="scan_history")
    product: Mapped["Product"] = relationship("Product", back_populates="scan_history")


class SavedProduct(Base):
    """Saved product model for user favorites."""

    __tablename__ = "saved_products"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), index=True)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="saved_products")
    product: Mapped["Product"] = relationship("Product", back_populates="saved_products")


class KeepaSnapshot(Base):
    """Raw Keepa API snapshot storage."""

    __tablename__ = "keepa_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    asin: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(20), nullable=False, default="keepa")
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=func.now(), index=True)
