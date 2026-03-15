from abc import abstractmethod
from uuid import UUID

from interviews.domain.plan.models import Plan, Question
from interviews.domain.plan.schemas import CreatePlanSchema, PlanFilters
from interviews.infrastructure.repository.base_repository import AbstractRepository


class PlanRepository(AbstractRepository[Plan]):
    @abstractmethod
    async def find_all_by_user_id(self, user_id: UUID, filters: PlanFilters) -> list[Plan]:
        raise NotImplementedError

    @abstractmethod
    async def find_one_or_none(self, item_id: int) -> Plan | None:
        raise NotImplementedError

    @abstractmethod
    async def find_one(self, item_id: int) -> Plan:
        raise NotImplementedError

    @abstractmethod
    async def update_one(self, item_id: int, data: dict) -> Plan:
        raise NotImplementedError

    @abstractmethod
    async def add_one_with_questions(self, data: CreatePlanSchema, user_id: UUID) -> Plan:
        raise NotImplementedError


class QuestionRepository(AbstractRepository[Question]):
    @abstractmethod
    async def reorder(self, items: list[dict]) -> None:
        raise NotImplementedError
