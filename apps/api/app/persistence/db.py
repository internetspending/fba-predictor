"""Database connection and session management."""

from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from apps.api.app.core.config import settings

# Lazy engine creation - will be created on first use
_engine = None
_async_session_local = None


def get_engine():
    """Get or create the async engine (lazy initialization)."""
    global _engine
    if _engine is None:
        # Ensure we're using psycopg (psycopg3) if the URL doesn't specify a driver
        db_url = settings.database_url
        if db_url.startswith("postgresql://") and "+psycopg" not in db_url:
            db_url = db_url.replace("postgresql://", "postgresql+psycopg://", 1)
        _engine = create_async_engine(db_url, echo=False)
    return _engine


def get_session_local():
    """Get or create the async session factory (lazy initialization)."""
    global _async_session_local
    if _async_session_local is None:
        _async_session_local = async_sessionmaker(
            get_engine(), class_=AsyncSession, expire_on_commit=False
        )
    return _async_session_local


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session."""
    session_factory = get_session_local()
    async with session_factory() as session:
        yield session


async def init_db() -> None:
    """Initialize database connection."""
    try:
        db_engine = get_engine()
        async with db_engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception:
        # Database may not be available yet - this is OK for startup
        # The health check endpoint will report the actual status
        pass


async def close_db() -> None:
    """Close database connection."""
    global _engine
    if _engine is not None:
        await _engine.dispose()
        _engine = None
