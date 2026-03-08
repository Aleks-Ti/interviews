from abc import abstractmethod
from uuid import UUID

from interviews.domain.plan.models import Plan, Question
from interviews.domain.plan.schemas import PlanFilters
from interviews.infrastructure.database.models.users import Roles
from interviews.infrastructure.repository.base_repository import AbstractRepository


class PlanRepository(AbstractRepository[Plan]):
    Id = UUID | int

    @abstractmethod
    async def find_all_by_user_id(self, user_id: UUID, filters: PlanFilters) -> list[Plan]:
        raise NotImplementedError

    @abstractmethod
    async def find_one_or_none(self, item_id: Id) -> Plan | None:
        raise NotImplementedError

    @abstractmethod
    async def update_all(self, data: dict) -> list[Plan]:
        raise NotImplementedError

    @abstractmethod
    async def find_one(self, item_id: UUID | int) -> Plan:
        raise NotImplementedError

    @abstractmethod
    async def update_one(self, item_id: UUID | int, data: dict) -> Plan:
        raise NotImplementedError


class QuestionRepository(AbstractRepository[Question]): ...
