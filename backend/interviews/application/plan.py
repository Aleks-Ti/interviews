from uuid import UUID

from interviews.application.uow import AbstractUnitOfWork
from interviews.domain.plan.models import Plan, Question
from interviews.domain.plan.schemas import (
    CreatePlanSchema,
    CreateQuestionSchema,
    PlanFilters,
    UpdatePlanSchema,
    UpdateQuestionSchema,
)
from interviews.domain.plan.service import PlanService, QuestionService


class PlanUseCases:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self.uow = uow

    def _service(self, uow: AbstractUnitOfWork) -> PlanService:
        return PlanService(uow.plans)

    def _question_service(self, uow: AbstractUnitOfWork) -> QuestionService:
        return QuestionService(uow.plans, uow.questions)

    async def get_plans(self, user_id: UUID, filters: PlanFilters) -> list[Plan]:
        async with self.uow as uow:
            return await self._service(uow).get_plans(user_id, filters)

    async def get_plan(self, plan_id: int, user_id: UUID) -> Plan:
        async with self.uow as uow:
            return await self._service(uow).get_plan(plan_id, user_id)

    async def create_plan(self, data: CreatePlanSchema, user_id: UUID) -> Plan:
        async with self.uow as uow:
            plan = await self._service(uow).create_plan(data, user_id)
            await uow.commit()
            return plan

    async def update_plan(self, plan_id: int, data: UpdatePlanSchema, user_id: UUID) -> Plan:
        async with self.uow as uow:
            plan = await self._service(uow).update_plan(plan_id, data, user_id)
            await uow.commit()
            return plan

    async def delete_plan(self, plan_id: int, user_id: UUID) -> None:
        async with self.uow as uow:
            await self._service(uow).delete_plan(plan_id, user_id)
            await uow.commit()

    async def fork_plan(self, plan_id: int, user_id: UUID) -> Plan:
        async with self.uow as uow:
            plan = await self._service(uow).fork_plan(plan_id, user_id)
            await uow.commit()
            return plan

    async def publish_plan(self, plan_id: int, user_id: UUID) -> Plan:
        async with self.uow as uow:
            plan = await self._service(uow).publish_plan(plan_id, user_id)
            await uow.commit()
            return plan

    async def add_question(self, plan_id: int, data: CreateQuestionSchema, user_id: UUID) -> Question:
        async with self.uow as uow:
            question = await self._question_service(uow).add_question(plan_id, data, user_id)
            await uow.commit()
            return question

    async def update_question(
        self, plan_id: int, question_id: int, data: UpdateQuestionSchema, user_id: UUID
    ) -> Question:
        async with self.uow as uow:
            question = await self._question_service(uow).update_question(plan_id, question_id, data, user_id)
            await uow.commit()
            return question

    async def delete_question(self, plan_id: int, question_id: int, user_id: UUID) -> None:
        async with self.uow as uow:
            await self._question_service(uow).delete_question(plan_id, question_id, user_id)
            await uow.commit()
