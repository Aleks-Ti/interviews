from sqlalchemy.ext.asyncio import AsyncSession

from interwiews.application.uow import AbstractUnitOfWork
from interwiews.infrastructure.database.connection import async_session_maker
from interwiews.infrastructure.repository.persistence.user import PostgresAuthUserRepository, PostgresUserRepository


class SQLAlchemyUnitOfWork(AbstractUnitOfWork):
    async def __aenter__(self) -> "SQLAlchemyUnitOfWork":
        self._session: AsyncSession = async_session_maker()
        self.users = PostgresUserRepository(self._session)
        self.auth_users = PostgresAuthUserRepository(self._session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type is not None:
            await self.rollback()
        await self._session.close()

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()
