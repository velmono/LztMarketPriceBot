from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from config import settings


_engine = create_async_engine(
    url = settings.DATABASE_SQLLITE_URL,
)


_async_session = async_sessionmaker(
    bind = _engine,
    class_ = AsyncSession,
    expire_on_commit = False
)


@asynccontextmanager
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with _async_session() as session:
        yield session