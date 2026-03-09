from uuid import UUID

from interviews.domain.interview.exceptions import InterviewInvalidStatus, InterviewNotFound
from interviews.domain.interview.models import Answer, Interview, InterviewStatus
from interviews.domain.interview.repository import AnswerRepository, InterviewRepository
from interviews.domain.interview.schemas import InterviewFilters, StartInterviewSchema, SubmitAnswerSchema
from interviews.domain.plan.exceptions import PlanNotFound
from interviews.domain.plan.models import PlanStatus
from interviews.domain.plan.repository import PlanRepository


class InterviewService:
    def __init__(self, interview_repository: InterviewRepository, plan_repository: PlanRepository) -> None:
        self.interview_repository = interview_repository
        self.plan_repository = plan_repository

    async def get_interviews(self, user_id: UUID, filters: InterviewFilters) -> list[Interview]:
        return await self.interview_repository.find_all_by_user_id(user_id, filters)

    async def get_interview(self, interview_id: int, user_id: UUID) -> Interview:
        interview = await self.interview_repository.find_one_or_none(interview_id)
        if interview is None or interview.conducted_by != user_id:
            raise InterviewNotFound
        return interview

    async def start_interview(self, data: StartInterviewSchema, user_id: UUID) -> Interview:
        plan = await self.plan_repository.find_one_or_none(data.plan_id)
        if plan is None or plan.created_by_user_id != user_id:
            raise PlanNotFound
        if plan.status == PlanStatus.draft:
            await self.plan_repository.update_one(data.plan_id, {"status": PlanStatus.published})
        return await self.interview_repository.add_one({
            "plan_id": data.plan_id,
            "candidate_name": data.candidate_name,
            "type": data.type,
            "status": InterviewStatus.pending,
            "conducted_by": user_id,
        })

    async def begin_interview(self, interview_id: int, user_id: UUID) -> Interview:
        interview = await self.interview_repository.find_one_or_none(interview_id)
        if interview is None or interview.conducted_by != user_id:
            raise InterviewNotFound
        if interview.status != InterviewStatus.pending:
            raise InterviewInvalidStatus
        return await self.interview_repository.update_one(interview_id, {"status": InterviewStatus.in_progress})

    async def complete_interview(self, interview_id: int, user_id: UUID) -> Interview:
        interview = await self.interview_repository.find_one_or_none(interview_id)
        if interview is None or interview.conducted_by != user_id:
            raise InterviewNotFound
        if interview.status != InterviewStatus.in_progress:
            raise InterviewInvalidStatus
        return await self.interview_repository.update_one(interview_id, {"status": InterviewStatus.completed})

    async def delete_interview(self, interview_id: int, user_id: UUID) -> None:
        interview = await self.interview_repository.find_one_or_none(interview_id)
        if interview is None or interview.conducted_by != user_id:
            raise InterviewNotFound
        await self.interview_repository.delete_one(interview_id)


class AnswerService:
    def __init__(self, interview_repository: InterviewRepository, answer_repository: AnswerRepository) -> None:
        self.interview_repository = interview_repository
        self.answer_repository = answer_repository

    async def submit_answer(self, interview_id: int, data: SubmitAnswerSchema, user_id: UUID) -> Answer:
        interview = await self.interview_repository.find_one_or_none(interview_id)
        if interview is None or interview.conducted_by != user_id:
            raise InterviewNotFound
        if interview.status != InterviewStatus.in_progress:
            raise InterviewInvalidStatus
        return await self.answer_repository.add_one({
            "interview_id": interview_id,
            "question_id": data.question_id,
            "answer": data.answer,
            "transcript": data.transcript,
            "audio_path": data.audio_path,
        })
