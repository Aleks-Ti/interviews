from abc import ABC, abstractmethod

from interviews.domain.analysis.repository import AnalysisRepository
from interviews.domain.auth.repository import AuthUserRepository
from interviews.domain.interview.repository import AnswerRepository, InterviewRepository
from interviews.domain.plan.repository import PlanRepository, QuestionRepository
from interviews.domain.user.repository import UserRepository


class AbstractUnitOfWork(ABC):
    users: UserRepository
    auth_users: AuthUserRepository
    plans: PlanRepository
    questions: QuestionRepository
    interviews: InterviewRepository
    answers: AnswerRepository
    analyses: AnalysisRepository

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
