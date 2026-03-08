from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from interviews.domain.plan.repository import PlanRepository
from interviews.domain.plan.models import Plan as DomainPlan
from interviews.domain.plan.models import Question as DomainQuestion
from interviews.domain.user.repository import UserRepository
from interviews.domain.plan.schemas import PlanFilters
from interviews.infrastructure.database.models.plans import Plans as OrmPlans
from interviews.infrastructure.repository.base_repository import BaseImplementationRepository


class PostgresPlanRepository(BaseImplementationRepository[OrmPlans, DomainPlan], PlanRepository):
    model: type[OrmPlans] = OrmPlans

    def _to_domain(self, orm_obj: OrmPlans) -> DomainPlan:
        return DomainPlan(
            id=orm_obj.id,
            name=orm_obj.name,
            questions=[DomainQuestion(id=q.id, text=q.text) for q in orm_obj.questions],
            description=orm_obj.description,
        )

    async def find_all_by_user_id(self, user_id: UUID, filters: PlanFilters) -> list[DomainPlan]:
        skip = (filters.page - 1) * filters.page_size
        stmt = select(self.model).options(selectinload(self.model.questions)).where(self.model.created_by_user_id == user_id)

        stmt = stmt.limit(filters.page_size).offset(skip)
        res = await self._session.execute(stmt)
        return self._to_domain_many(res.scalars().all())
