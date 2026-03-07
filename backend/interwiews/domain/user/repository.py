from abc import abstractmethod
from collections.abc import Sequence
from uuid import UUID

from interwiews.domain.user.models import User
from interwiews.domain.user.schemas import UserFilters
from interwiews.infrastructure.database.models.user import Role
from interwiews.infrastructure.repository.base_repository import AbstractRepository


class UserRepository(AbstractRepository[User]):
    Id = UUID | int

    @abstractmethod
    async def find_all_by_filter(self, query_params: UserFilters) -> Sequence[User]:
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


class RoleRepository(AbstractRepository[Role]): ...
