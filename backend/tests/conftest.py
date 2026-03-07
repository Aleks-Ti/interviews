import os
import uuid

os.environ.setdefault("PG_USER", "postgres")
os.environ.setdefault("PG_PASSWORD", "postgres")
os.environ.setdefault("PG_HOST", "localhost")
os.environ.setdefault("PG_PORT", "5523")
os.environ.setdefault("PG_DB", "postgres_db")
os.environ.setdefault("TOKEN_SECRET_KEY", "test_secret")

import psycopg2
import pytest
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from interwiews.infrastructure.database.base_model import metadata

# Import all models so metadata is populated
import interwiews.infrastructure.database.models.user  # noqa: F401
import interwiews.infrastructure.database.models.post  # noqa: F401
import interwiews.infrastructure.database.models.comment  # noqa: F401

PG_USER = os.environ["PG_USER"]
PG_PASSWORD = os.environ["PG_PASSWORD"]
PG_HOST = os.environ["PG_HOST"]
PG_PORT = os.environ["PG_PORT"]
PG_DB = os.environ["PG_DB"]

TEST_DB_NAME = f"{PG_DB}_test"
TEST_DB_URL = f"postgresql+asyncpg://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{TEST_DB_NAME}"


@pytest.fixture(scope="session", autouse=True)
def create_test_database():
    conn = psycopg2.connect(
        dbname="postgres",
        user=PG_USER,
        password=PG_PASSWORD,
        host=PG_HOST,
        port=PG_PORT,
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    try:
        cur.execute(f"CREATE DATABASE {TEST_DB_NAME}")
    except psycopg2.errors.DuplicateDatabase:
        pass
    cur.close()
    conn.close()


@pytest.fixture(scope="session")
async def test_engine(create_test_database):
    engine = create_async_engine(TEST_DB_URL)
    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)
        await conn.run_sync(metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)
    await engine.dispose()


@pytest.fixture(scope="session")
async def seed_roles(test_engine):
    from sqlalchemy import insert
    from interwiews.infrastructure.database.models.user import Role

    async with async_sessionmaker(test_engine, expire_on_commit=False)() as session:
        async with session.begin():
            await session.execute(
                insert(Role).values([
                    {"id": 1, "name": "admin"},
                    {"id": 2, "name": "owner"},
                    {"id": 3, "name": "user"},
                ])
            )


@pytest.fixture(scope="session")
async def test_user_id(seed_roles, test_engine):
    from sqlalchemy import insert
    from interwiews.infrastructure.database.models.user import User

    user_id = uuid.uuid4()
    async with async_sessionmaker(test_engine, expire_on_commit=False)() as session:
        async with session.begin():
            await session.execute(
                insert(User).values(
                    id=user_id,
                    email="test@example.com",
                    password="$2b$12$hashedpassword",
                    role_id=3,
                    is_active=True,
                    is_allowed_comment=True,
                )
            )
    return user_id


@pytest.fixture(scope="function")
async def db_session(test_engine) -> AsyncSession:
    async with async_sessionmaker(test_engine, expire_on_commit=False)() as session:
        await session.begin()
        yield session
        await session.rollback()
