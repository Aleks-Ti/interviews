from abc import abstractmethod

from interviews.domain.analysis.models import Analysis
from interviews.infrastructure.repository.base_repository import AbstractRepository


class AnalysisRepository(AbstractRepository[Analysis]):
    @abstractmethod
    async def find_by_answer_id(self, answer_id: int) -> Analysis | None:
        raise NotImplementedError
