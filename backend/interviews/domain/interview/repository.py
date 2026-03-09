from abc import abstractmethod
from uuid import UUID

from interviews.domain.interview.models import Answer, Interview
from interviews.domain.interview.schemas import InterviewFilters
from interviews.infrastructure.repository.base_repository import AbstractRepository


class InterviewRepository(AbstractRepository[Interview]):
    @abstractmethod
    async def find_all_by_user_id(self, user_id: UUID, filters: InterviewFilters) -> list[Interview]:
        raise NotImplementedError

    @abstractmethod
    async def find_one_or_none(self, item_id: int) -> Interview | None:
        raise NotImplementedError

    @abstractmethod
    async def find_one(self, item_id: int) -> Interview:
        raise NotImplementedError

    @abstractmethod
    async def update_one(self, item_id: int, data: dict) -> Interview:
        raise NotImplementedError


class AnswerRepository(AbstractRepository[Answer]):
    pass
