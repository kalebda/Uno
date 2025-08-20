# app/db/session.py
from app.db.base import AsyncSessionLocal, SessionLocal


# Sync dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Async dependency
async def get_async_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
