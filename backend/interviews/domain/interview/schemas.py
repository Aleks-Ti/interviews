from pydantic import Field

from interviews.core.schemas import PreBasePydanticModel
from interviews.domain.analysis.schemas import GetAnalysisSchema


class InterviewFilters(PreBasePydanticModel):
    page: int = Field(1, gt=0)
    page_size: int = Field(10, gt=0)


class StartInterviewSchema(PreBasePydanticModel):
    plan_id: int
    candidate_name: str
    type: str


class SubmitAnswerSchema(PreBasePydanticModel):
    question_id: int
    answer: str
    transcript: str | None = None
    audio_path: str | None = None


class GetAnswerSchema(PreBasePydanticModel):
    id: int
    question_id: int
    answer: str
    transcript: str | None
    audio_path: str | None
    analysis: GetAnalysisSchema | None = None


class GetInterviewSchema(PreBasePydanticModel):
    id: int
    candidate_name: str
    type: str
    status: str
    plan_id: int
    answers: list[GetAnswerSchema]
