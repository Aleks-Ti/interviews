from uuid import UUID

from interviews.domain.analysis.exceptions import AnalysisAlreadyExists, AnswerNotFound
from interviews.domain.analysis.models import Analysis
from interviews.domain.analysis.repository import AnalysisRepository
from interviews.domain.interview.exceptions import InterviewNotFound
from interviews.domain.interview.repository import AnswerRepository, InterviewRepository
from interviews.domain.plan.repository import QuestionRepository
from interviews.providers.base import AIProvider


class AnalysisService:
    def __init__(
        self,
        interview_repository: InterviewRepository,
        answer_repository: AnswerRepository,
        question_repository: QuestionRepository,
        analysis_repository: AnalysisRepository,
        ai: AIProvider,
    ) -> None:
        self.interview_repository = interview_repository
        self.answer_repository = answer_repository
        self.question_repository = question_repository
        self.analysis_repository = analysis_repository
        self.ai = ai

    async def analyze_answer(self, interview_id: int, answer_id: int, user_id: UUID) -> Analysis:
        interview = await self.interview_repository.find_one_or_none(interview_id)
        if interview is None or interview.conducted_by != user_id:
            raise InterviewNotFound

        answer = await self.answer_repository.find_one_or_none(answer_id)
        if answer is None or answer.interview_id != interview_id:
            raise AnswerNotFound

        existing = await self.analysis_repository.find_by_answer_id(answer_id)
        if existing is not None:
            raise AnalysisAlreadyExists

        question = await self.question_repository.find_one(answer.question_id)

        result = await self.ai.analyze_answer(
            question=question.text,
            answer=answer.answer,
            criteria=question.criteria,
        )

        return await self.analysis_repository.add_one({
            "answer_id": answer_id,
            "score": result.score,
            "summary": result.summary,
            "strengths": result.strengths,
            "weaknesses": result.weaknesses,
            "recomendation": result.recommendation,
        })

    async def analyze_all(self, interview_id: int, user_id: UUID) -> list[Analysis]:
        interview = await self.interview_repository.find_one_or_none(interview_id)
        if interview is None or interview.conducted_by != user_id:
            raise InterviewNotFound

        results = []
        for answer in interview.answers:
            existing = await self.analysis_repository.find_by_answer_id(answer.id)
            if existing is not None:
                results.append(existing)
                continue

            question = await self.question_repository.find_one(answer.question_id)
            result = await self.ai.analyze_answer(
                question=question.text,
                answer=answer.answer,
                criteria=question.criteria,
            )
            analysis = await self.analysis_repository.add_one({
                "answer_id": answer.id,
                "score": result.score,
                "summary": result.summary,
                "strengths": result.strengths,
                "weaknesses": result.weaknesses,
                "recomendation": result.recommendation,
            })
            results.append(analysis)

        return results
