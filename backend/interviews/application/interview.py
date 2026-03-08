from interviews.application.uow import AbstractUnitOfWork
from interviews.domain.auth.models import User
from interviews.domain.interview.models import Interview
from interviews.domain.interview.schemas import StartInterviewSchema
from interviews.domain.plan.service import PlanService


class InterviewUseCases:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self.uow = uow

    async def start_interview(self, data: StartInterviewSchema, current_user: User) -> Interview:
        async with self.uow as uow:
            plan = await PlanService(uow.plans).get_plan(data.plan_id)
            interview = await InterviewService(uow.interviews).create(data, plan.id, current_user.id)
            await uow.commit()
            return interview
