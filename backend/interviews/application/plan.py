from uuid import UUID

from interviews.application.uow import AbstractUnitOfWork
from interviews.domain.plan.models import Plan
from interviews.domain.plan.schemas import CreatePlanSchema, PlanFilters, UpdatePlanSchema
from interviews.domain.plan.service import PlanService


class PlanUseCases:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self.uow = uow

    async def get_plans(self, user_id: UUID, filters: PlanFilters) -> list[Plan]:
        async with self.uow as uow:
            service = PlanService(uow.plans)
            return await service.get_plans(user_id, filters)

    async def get_plan(self, plan_id: int, user_id: UUID) -> Plan:
        async with self.uow as uow:
            service = PlanService(uow.plans)
            return await service.get_plan(plan_id, user_id)

    async def create_plan(self, data: CreatePlanSchema, user_id: UUID) -> Plan:
        async with self.uow as uow:
            service = PlanService(uow.plans)
            plan = await service.create_plan(data, user_id)
            await uow.commit()
            return plan

    async def update_plan(self, plan_id: int, data: UpdatePlanSchema, user_id: UUID) -> Plan:
        async with self.uow as uow:
            service = PlanService(uow.plans)
            plan = await service.update_plan(plan_id, data, user_id)
            await uow.commit()
            return plan

    async def delete_plan(self, plan_id: int, user_id: UUID) -> None:
        async with self.uow as uow:
            service = PlanService(uow.plans)
            await service.delete_plan(plan_id, user_id)
            await uow.commit()
