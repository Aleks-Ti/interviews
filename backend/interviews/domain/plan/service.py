from uuid import UUID

from interviews.domain.plan.exceptions import PlanNotEditable, PlanNotFound, QuestionNotFound
from interviews.domain.plan.models import Plan, PlanStatus, Question
from interviews.domain.plan.repository import PlanRepository, QuestionRepository
from interviews.domain.plan.schemas import (
    CreatePlanSchema,
    CreateQuestionSchema,
    PlanFilters,
    UpdatePlanSchema,
    UpdateQuestionSchema,
)


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
        if plan.status != PlanStatus.draft:
            raise PlanNotEditable
        return await self.plan_repository.update_one(plan_id, data.model_dump(exclude_none=True))

    async def delete_plan(self, plan_id: int, user_id: UUID) -> None:
        plan = await self.plan_repository.find_one_or_none(plan_id)
        if plan is None or plan.created_by_user_id != user_id:
            raise PlanNotFound
        await self.plan_repository.delete_one(plan_id)

    async def fork_plan(self, plan_id: int, user_id: UUID) -> Plan:
        plan = await self.plan_repository.find_one_or_none(plan_id)
        if plan is None or plan.created_by_user_id != user_id:
            raise PlanNotFound
        fork_data = CreatePlanSchema(
            name=f"{plan.name} (copy)",
            description=plan.description,
            questions=[
                CreateQuestionSchema(text=q.text, type=q.type, criteria=q.criteria)
                for q in plan.questions
            ],
        )
        return await self.plan_repository.add_one_with_questions(fork_data, user_id)

    async def publish_plan(self, plan_id: int, user_id: UUID) -> Plan:
        plan = await self.plan_repository.find_one_or_none(plan_id)
        if plan is None or plan.created_by_user_id != user_id:
            raise PlanNotFound
        if plan.status == PlanStatus.published:
            return plan
        return await self.plan_repository.update_one(plan_id, {"status": PlanStatus.published})


class QuestionService:
    def __init__(self, plan_repository: PlanRepository, question_repository: QuestionRepository) -> None:
        self.plan_repository = plan_repository
        self.question_repository = question_repository

    async def _get_editable_plan(self, plan_id: int, user_id: UUID) -> Plan:
        plan = await self.plan_repository.find_one_or_none(plan_id)
        if plan is None or plan.created_by_user_id != user_id:
            raise PlanNotFound
        if plan.status != PlanStatus.draft:
            raise PlanNotEditable
        return plan

    async def add_question(self, plan_id: int, data: CreateQuestionSchema, user_id: UUID) -> Question:
        plan = await self._get_editable_plan(plan_id, user_id)
        next_position = max((q.position for q in plan.questions), default=-1) + 1
        return await self.question_repository.add_one(
            {"text": data.text, "type": data.type, "criteria": data.criteria, "plan_id": plan_id, "position": next_position}
        )

    async def update_question(
        self, plan_id: int, question_id: int, data: UpdateQuestionSchema, user_id: UUID
    ) -> Question:
        await self._get_editable_plan(plan_id, user_id)
        question = await self.question_repository.find_one_or_none(question_id)
        if question is None or question.plan_id != plan_id:
            raise QuestionNotFound
        return await self.question_repository.update_one(question_id, data.model_dump(exclude_none=True))

    async def delete_question(self, plan_id: int, question_id: int, user_id: UUID) -> None:
        await self._get_editable_plan(plan_id, user_id)
        question = await self.question_repository.find_one_or_none(question_id)
        if question is None or question.plan_id != plan_id:
            raise QuestionNotFound
        await self.question_repository.delete_one(question_id)

    async def reorder_questions(self, plan_id: int, items: list[dict], user_id: UUID) -> None:
        await self._get_editable_plan(plan_id, user_id)
        await self.question_repository.reorder(items)
