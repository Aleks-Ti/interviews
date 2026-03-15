from sqlalchemy import update

from interviews.domain.plan.models import Question as DomainQuestion
from interviews.domain.plan.repository import QuestionRepository
from interviews.infrastructure.database.models.questions import Questions as OrmQuestions
from interviews.infrastructure.repository.base_repository import BaseImplementationRepository


class PostgresQuestionRepository(BaseImplementationRepository[OrmQuestions, DomainQuestion], QuestionRepository):
    model: type[OrmQuestions] = OrmQuestions

    def _to_domain(self, orm_obj: OrmQuestions) -> DomainQuestion:
        return DomainQuestion(
            id=orm_obj.id,
            text=orm_obj.text,
            type=orm_obj.type,
            criteria=orm_obj.criteria,
            plan_id=orm_obj.plan_id,
            date_create=orm_obj.date_create,
            date_update=orm_obj.date_update,
            position=orm_obj.position,
            expected_answer=orm_obj.expected_answer,
        )

    async def reorder(self, items: list[dict]) -> None:
        for item in items:
            stmt = update(self.model).where(self.model.id == item["id"]).values(position=item["position"])
            await self._session.execute(stmt)
