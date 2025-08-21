# app/db/init_db.py
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.crud.user import user_crud
from app.db.base import AsyncSessionLocal


async def init_db(db: AsyncSession) -> None:
    """Initialize database with default user."""
    try:
        # Create default user for testing
        default_user = await user_crud.get_or_create_default_user(db)
        print(f"Default user ready: {default_user.email}")

    except Exception as e:
        print(f"Error during database initialization: {e}")
        await db.rollback()
        raise


async def initialize_data():
    """Async function to initialize data."""
    async with AsyncSessionLocal() as db:
        await init_db(db)


def init_default_user():
    """Synchronous wrapper for async initialization."""
    try:
        asyncio.run(initialize_data())
    except Exception as e:
        print(f"Failed to initialize default user: {e}")
