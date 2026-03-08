from abc import abstractmethod
from collections.abc import Sequence
from uuid import UUID

from interviews.domain.user.models import User
from interviews.domain.user.schemas import UserFilters
from interviews.infrastructure.database.models.users import Roles
from interviews.infrastructure.repository.base_repository import AbstractRepository


class UserRepository(AbstractRepository[User]):
    Id = UUID | int

    @abstractmethod
    async def find_all_by_filter(self, query_params: UserFilters) -> list[User]:
        raise NotImplementedError

    @abstractmethod
    async def find_one_or_none(self, item_id: Id) -> User | None:
        raise NotImplementedError

    @abstractmethod
    async def update_all(self, data: dict) -> list[User]:
        raise NotImplementedError

    @abstractmethod
    async def find_by_email(self, user_email: str) -> User | None:
        raise NotImplementedError

    @abstractmethod
    async def find_one(self, item_id: UUID | int) -> User:
        raise NotImplementedError

    @abstractmethod
    async def update_one(self, item_id: UUID | int, data: dict) -> User:
        raise NotImplementedError


class RoleRepository(AbstractRepository[Roles]): ...
