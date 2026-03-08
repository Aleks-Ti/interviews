from uuid import UUID

from interviews.domain.plan.exceptions import PlanNotFound
from interviews.domain.plan.models import Plan
from interviews.domain.plan.repository import PlanRepository
from interviews.domain.plan.schemas import CreatePlanSchema, PlanFilters, UpdatePlanSchema


class PlanService:
    def __init__(self, plan_repository: PlanRepository) -> None:
        self.plan_repository = plan_repository

    async def get_plans(self, user_id: UUID, filters: PlanFilters) -> list[Plan]:
        return await self.plan_repository.find_all_by_user_id(user_id, filters)

    async def get_plan(self, plan_id: int, user_id: UUID) -> Plan:
        plan = await self.plan_repository.find_one_or_none(plan_id)
        if plan is None or plan.created_by_user_id != user_id:
            raise PlanNotFound
        return plan

    async def create_plan(self, data: CreatePlanSchema, user_id: UUID) -> Plan:
        return await self.plan_repository.add_one_with_questions(data, user_id)

    async def update_plan(self, plan_id: int, data: UpdatePlanSchema, user_id: UUID) -> Plan:
        plan = await self.plan_repository.find_one_or_none(plan_id)
        if plan is None or plan.created_by_user_id != user_id:
            raise PlanNotFound
        update_data = data.model_dump(exclude_none=True)
        return await self.plan_repository.update_one(plan_id, update_data)

    async def delete_plan(self, plan_id: int, user_id: UUID) -> None:
        plan = await self.plan_repository.find_one_or_none(plan_id)
        if plan is None or plan.created_by_user_id != user_id:
            raise PlanNotFound
        await self.plan_repository.delete_one(plan_id)


class QuestionService: ...
