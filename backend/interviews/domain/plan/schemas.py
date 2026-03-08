from interviews.core.schemas import PreBasePydanticModel
from pydantic import Field


class PlanFilters(PreBasePydanticModel):
    page: int = Field(..., gt=0)
    page_size: int = Field(..., gt=0)


class GetQuestionSchema(PreBasePydanticModel):
    id: int
    text: str


class GetPlanSchema(PreBasePydanticModel):
    id: int
    name: str
    description: str | None
    questions: list[GetQuestionSchema]
