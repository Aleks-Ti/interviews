from interviews.domain.plan.models import Plan
from interviews.domain.plan.repository import PlanRepository
from interviews.domain.plan.schemas import PlanFilters
from interviews.domain.plan.models import User


class PlanService:
    def __init__(
        self,
        plan_repository: PlanRepository,
    ) -> None:
        self.plan_repository: PlanRepository = plan_repository

    async def get_plans(self, current_user: User, filters: PlanFilters) -> list[Plan]:
        plans = await self.plan_repository.find_all_by_user_id(current_user.id, filters)
        return plans


class QuestionService: ...
