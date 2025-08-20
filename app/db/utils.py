# app/db/utils.py
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy import text


async def check_db_connected(engine: AsyncEngine) -> bool:
    """Check if database is connected using async engine."""
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False
