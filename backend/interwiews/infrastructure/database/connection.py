import subprocess
from collections.abc import AsyncGenerator, Callable

from sqlalchemy.engine.url import URL
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine as _create_async_engine

from interwiews.common.configuration import conf


def create_async_engine(url: URL | str) -> AsyncEngine:
    return _create_async_engine(url=url, echo=conf.debug, pool_pre_ping=True)


async_session_maker: Callable[..., AsyncSession] = async_sessionmaker(
    bind=create_async_engine(conf.db.build_connection_str()), class_=AsyncSession, expire_on_commit=False
)


async def get_async_session() -> AsyncGenerator:
    async with async_session_maker() as session:
        yield session


async def migrate():
    subprocess.run("alembic upgrade head", shell=True, check=True)
