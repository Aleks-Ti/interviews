from uuid import UUID

from sqlalchemy import insert, select, update
from sqlalchemy.orm import selectinload

from interviews.domain.interview.models import Answer as DomainAnswer
from interviews.domain.interview.models import Interview as DomainInterview
from interviews.domain.interview.repository import AnswerRepository, InterviewRepository
from interviews.domain.interview.schemas import InterviewFilters
from interviews.infrastructure.database.models.answers import Answers as OrmAnswers
from interviews.infrastructure.database.models.interviews import Interviews as OrmInterviews
from interviews.infrastructure.repository.base_repository import BaseImplementationRepository


class PostgresInterviewRepository(
    BaseImplementationRepository[OrmInterviews, DomainInterview], InterviewRepository
):
    model: type[OrmInterviews] = OrmInterviews

    def _to_domain(self, orm_obj: OrmInterviews) -> DomainInterview:
        return DomainInterview(
            id=orm_obj.id,
            candidate_name=orm_obj.candidate_name,
            type=orm_obj.type,
            status=orm_obj.status,
            plan_id=orm_obj.plan_id,
            conducted_by=orm_obj.conducted_by,
            date_create=orm_obj.date_create,
            date_update=orm_obj.date_update,
            answers=[
                DomainAnswer(
                    id=a.id,
                    answer=a.answer,
                    audio_path=a.audio_path,
                    transcript=a.transcript,
                    question_id=a.question_id,
                    interview_id=a.interview_id,
                    date_create=a.date_create,
                    date_update=a.date_update,
                )
                for a in orm_obj.answers
            ],
        )

    async def add_one(self, data: dict) -> DomainInterview:
        stmt = insert(self.model).values(**data).returning(self.model.id)
        res = await self._session.execute(stmt)
        interview_id = res.scalar_one()
        return await self.find_one(interview_id)

    def _with_answers(self):
        return select(self.model).options(selectinload(self.model.answers))

    async def find_one(self, item_id: int) -> DomainInterview:
        stmt = self._with_answers().where(self.model.id == item_id)
        res = await self._session.execute(stmt)
        return self._to_domain(res.scalar_one())

    async def find_one_or_none(self, item_id: int) -> DomainInterview | None:
        stmt = self._with_answers().where(self.model.id == item_id)
        res = await self._session.execute(stmt)
        orm_obj = res.scalar_one_or_none()
        if orm_obj is None:
            return None
        return self._to_domain(orm_obj)

    async def update_one(self, item_id: int, data: dict) -> DomainInterview:
        stmt = update(self.model).where(self.model.id == item_id).values(**data)
        await self._session.execute(stmt)
        return await self.find_one(item_id)

    async def find_all_by_user_id(self, user_id: UUID, filters: InterviewFilters) -> list[DomainInterview]:
        skip = (filters.page - 1) * filters.page_size
        stmt = (
            self._with_answers()
            .where(self.model.conducted_by == user_id)
            .order_by(self.model.date_create.desc())
            .limit(filters.page_size)
            .offset(skip)
        )
        res = await self._session.execute(stmt)
        return self._to_domain_many(res.scalars().all())


class PostgresAnswerRepository(BaseImplementationRepository[OrmAnswers, DomainAnswer], AnswerRepository):
    model: type[OrmAnswers] = OrmAnswers

    def _to_domain(self, orm_obj: OrmAnswers) -> DomainAnswer:
        return DomainAnswer(
            id=orm_obj.id,
            answer=orm_obj.answer,
            audio_path=orm_obj.audio_path,
            transcript=orm_obj.transcript,
            question_id=orm_obj.question_id,
            interview_id=orm_obj.interview_id,
            date_create=orm_obj.date_create,
            date_update=orm_obj.date_update,
        )
