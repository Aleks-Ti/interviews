from uuid import UUID

from interviews.application.uow import AbstractUnitOfWork
from interviews.domain.interview.models import Answer, Interview
from interviews.domain.interview.schemas import InterviewFilters, StartInterviewSchema, SubmitAnswerSchema
from interviews.domain.interview.service import AnswerService, InterviewService


class InterviewUseCases:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self.uow = uow

    def _service(self, uow: AbstractUnitOfWork) -> InterviewService:
        return InterviewService(uow.interviews, uow.plans)

    def _answer_service(self, uow: AbstractUnitOfWork) -> AnswerService:
        return AnswerService(uow.interviews, uow.answers)

    async def get_interviews(self, user_id: UUID, filters: InterviewFilters) -> list[Interview]:
        async with self.uow as uow:
            return await self._service(uow).get_interviews(user_id, filters)

    async def get_interview(self, interview_id: int, user_id: UUID) -> Interview:
        async with self.uow as uow:
            return await self._service(uow).get_interview(interview_id, user_id)

    async def start_interview(self, data: StartInterviewSchema, user_id: UUID) -> Interview:
        async with self.uow as uow:
            interview = await self._service(uow).start_interview(data, user_id)
            await uow.commit()
            return interview

    async def begin_interview(self, interview_id: int, user_id: UUID) -> Interview:
        async with self.uow as uow:
            interview = await self._service(uow).begin_interview(interview_id, user_id)
            await uow.commit()
            return interview

    async def complete_interview(self, interview_id: int, user_id: UUID) -> Interview:
        async with self.uow as uow:
            interview = await self._service(uow).complete_interview(interview_id, user_id)
            await uow.commit()
            return interview

    async def delete_interview(self, interview_id: int, user_id: UUID) -> None:
        async with self.uow as uow:
            await self._service(uow).delete_interview(interview_id, user_id)
            await uow.commit()

    async def submit_answer(self, interview_id: int, data: SubmitAnswerSchema, user_id: UUID) -> Answer:
        async with self.uow as uow:
            answer = await self._answer_service(uow).submit_answer(interview_id, data, user_id)
            await uow.commit()
            return answer
