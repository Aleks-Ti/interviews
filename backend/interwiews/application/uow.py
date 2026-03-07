from abc import ABC, abstractmethod

from interwiews.domain.auth.repository import AuthUserRepository
from interwiews.domain.user.repository import UserRepository


class AbstractUnitOfWork(ABC):
    users: UserRepository
    auth_users: AuthUserRepository

    @abstractmethod
    async def __aenter__(self) -> "AbstractUnitOfWork":
        raise NotImplementedError

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        raise NotImplementedError

    @abstractmethod
    async def commit(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def rollback(self) -> None:
        raise NotImplementedError
