from sqlalchemy.ext.asyncio import create_async_engine
from app.db.database import Base
from app.db.database import engine

async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)