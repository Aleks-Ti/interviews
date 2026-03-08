from interviews.application.uow import AbstractUnitOfWork
from interviews.domain.plan.service import PlanService
from interviews.domain.plan.models import User, Plan
from interviews.domain.plan.schemas import PlanFilters


class PlanUseCases:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self.uow = uow

    async def get_plans(self, current_user: User, filters: PlanFilters) -> list[Plan]:
        async with self.uow as uow:
            service = PlanService(uow.plans)
            return await service.get_plans(current_user, filters)
