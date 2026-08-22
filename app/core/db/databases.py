from collections.abc import AsyncGenerator
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core import config

DATABASE_URL = config.DATABASE_URL

if DATABASE_URL.startswith("sqlite"):
    Path("data").mkdir(exist_ok=True)
    engine = create_async_engine(DATABASE_URL)
else:
    engine = create_async_engine(
        DATABASE_URL,
        pool_size=config.DB_CONNECTION_POOL_MAXSIZE,
        connect_args={"connect_timeout": config.DB_CONNECT_TIMEOUT},
    )

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        yield session
