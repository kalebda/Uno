# app/db/init_db.py
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.crud.user import user_crud
from app.db.base import AsyncSessionLocal
from app.schemas.user import UserCreate, UserType


async def init_db(db: AsyncSession) -> None:
    """Initialize database with first superuser."""
    try:
        # Check if superuser exists
        user = await user_crud.get_by_email(db, email=settings.FIRST_SUPERUSER)
        if not user:
            print(f"Creating superuser: {settings.FIRST_SUPERUSER}")
            user_in = UserCreate(
                email=settings.FIRST_SUPERUSER,
                password=settings.FIRST_SUPERUSER_PASSWORD,
                is_superuser=True,
                is_blog_admin=True,
                is_active=True,
                full_name="Initial Super User",
                user_type=UserType.ADMIN,
            )
            user = await user_crud.create(db, obj_in=user_in)
            await db.commit()
            print("Superuser created successfully")
        else:
            print("Superuser already exists")
    except Exception as e:
        print(f"Error during database initialization: {e}")
        await db.rollback()
        raise


async def initialize_data():
    """Async function to initialize data."""
    async with AsyncSessionLocal() as db:
        await init_db(db)


def init_superuser():
    """Synchronous wrapper for async initialization."""
    try:
        asyncio.run(initialize_data())
    except Exception as e:
        print(f"Failed to initialize superuser: {e}")
