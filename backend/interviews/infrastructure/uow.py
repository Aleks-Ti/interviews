from sqlalchemy.ext.asyncio import AsyncSession

from interviews.application.uow import AbstractUnitOfWork
from interviews.domain.analysis.repository import AnalysisRepository
from interviews.domain.interview.repository import AnswerRepository, InterviewRepository
from interviews.domain.plan.repository import PlanRepository, QuestionRepository
from interviews.infrastructure.database.connection import async_session_maker
from interviews.infrastructure.repository.persistence.analysis import PostgresAnalysisRepository
from interviews.infrastructure.repository.persistence.interview import PostgresAnswerRepository, PostgresInterviewRepository
from interviews.infrastructure.repository.persistence.plan import PostgresPlanRepository
from interviews.infrastructure.repository.persistence.question import PostgresQuestionRepository
from interviews.infrastructure.repository.persistence.user import PostgresAuthUserRepository, PostgresUserRepository


class SQLAlchemyUnitOfWork(AbstractUnitOfWork):
    async def __aenter__(self) -> "SQLAlchemyUnitOfWork":
        self._session: AsyncSession = async_session_maker()
        self.users = PostgresUserRepository(self._session)
        self.auth_users = PostgresAuthUserRepository(self._session)
        self.plans = PostgresPlanRepository(self._session)
        self.questions = PostgresQuestionRepository(self._session)
        self.interviews = PostgresInterviewRepository(self._session)
        self.answers = PostgresAnswerRepository(self._session)
        self.analyses = PostgresAnalysisRepository(self._session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type is not None:
            await self.rollback()
        await self._session.close()

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()
