from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserCreate


class UserCRUD:
    """CRUD operations for User model"""
    
    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """Get user by email"""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_id(self, db: AsyncSession, user_id: str) -> Optional[User]:
        """Get user by ID"""
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    
    async def create(self, db: AsyncSession, obj_in: UserCreate) -> User:
        """Create new user"""
        db_obj = User(
            id=obj_in.email,  # Using email as ID for simplicity
            email=obj_in.email,
            full_name=obj_in.full_name,
            is_superuser=obj_in.is_superuser,
            is_active=obj_in.is_active
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_or_create_default_user(self, db: AsyncSession) -> User:
        """Get or create default user for testing"""
        from app.core.config import settings

        user = await self.get_by_email(db, settings.DEFAULT_USER_EMAIL)

        if not user:
            user_in = UserCreate(
                email=settings.DEFAULT_USER_EMAIL,
                full_name=settings.DEFAULT_USER_NAME,
                is_superuser=settings.DEFAULT_USER_SUPERUSER,
                is_active=settings.DEFAULT_USER_ACTIVE
            )
            user = await self.create(db, user_in)

        return user


user_crud = UserCRUD()
