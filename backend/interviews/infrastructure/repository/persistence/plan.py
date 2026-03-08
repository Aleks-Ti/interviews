from uuid import UUID

from sqlalchemy import delete, insert, select, update
from sqlalchemy.orm import selectinload

from interviews.domain.plan.models import Plan as DomainPlan
from interviews.domain.plan.models import Question as DomainQuestion
from interviews.domain.plan.repository import PlanRepository
from interviews.domain.plan.schemas import CreatePlanSchema, PlanFilters
from interviews.infrastructure.database.models.plans import Plans as OrmPlans
from interviews.infrastructure.database.models.questions import Questions as OrmQuestions
from interviews.infrastructure.repository.base_repository import BaseImplementationRepository


class PostgresPlanRepository(BaseImplementationRepository[OrmPlans, DomainPlan], PlanRepository):
    model: type[OrmPlans] = OrmPlans

    def _to_domain(self, orm_obj: OrmPlans) -> DomainPlan:
        return DomainPlan(
            id=orm_obj.id,
            name=orm_obj.name,
            description=orm_obj.description,
            created_by_user_id=orm_obj.created_by_user_id,
            date_create=orm_obj.date_create,
            date_update=orm_obj.date_update,
            questions=[
                DomainQuestion(
                    id=q.id,
                    text=q.text,
                    type=q.type,
                    criteria=q.criteria,
                    plan_id=q.plan_id,
                    date_create=q.date_create,
                    date_update=q.date_update,
                )
                for q in orm_obj.questions
            ],
        )

    def _with_questions(self):
        return select(self.model).options(selectinload(self.model.questions))

    async def find_one(self, item_id: int) -> DomainPlan:
        stmt = self._with_questions().where(self.model.id == item_id)
        res = await self._session.execute(stmt)
        return self._to_domain(res.scalar_one())

    async def find_one_or_none(self, item_id: int) -> DomainPlan | None:
        stmt = self._with_questions().where(self.model.id == item_id)
        res = await self._session.execute(stmt)
        orm_obj = res.scalar_one_or_none()
        if orm_obj is None:
            return None
        return self._to_domain(orm_obj)

    async def update_one(self, item_id: int, data: dict) -> DomainPlan:
        stmt = update(self.model).where(self.model.id == item_id).values(**data)
        await self._session.execute(stmt)
        return await self.find_one(item_id)

    async def add_one_with_questions(self, data: CreatePlanSchema, user_id: UUID) -> DomainPlan:
        plan_stmt = (
            insert(self.model)
            .values(name=data.name, description=data.description, created_by_user_id=user_id)
            .returning(self.model.id)
        )
        res = await self._session.execute(plan_stmt)
        plan_id = res.scalar_one()

        if data.questions:
            questions_data = [
                {"text": q.text, "type": q.type, "criteria": q.criteria, "plan_id": plan_id}
                for q in data.questions
            ]
            await self._session.execute(insert(OrmQuestions).values(questions_data))

        return await self.find_one(plan_id)

    async def find_all_by_user_id(self, user_id: UUID, filters: PlanFilters) -> list[DomainPlan]:
        skip = (filters.page - 1) * filters.page_size
        stmt = (
            self._with_questions()
            .where(self.model.created_by_user_id == user_id)
            .limit(filters.page_size)
            .offset(skip)
        )
        res = await self._session.execute(stmt)
        return self._to_domain_many(res.scalars().all())
