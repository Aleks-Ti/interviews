from interviews.core.schemas import PreBasePydanticModel
from pydantic import Field


class PlanFilters(PreBasePydanticModel):
    page: int = Field(1, gt=0)
    page_size: int = Field(10, gt=0)


class CreateQuestionSchema(PreBasePydanticModel):
    text: str
    type: str
    criteria: list[str]


class UpdatePlanSchema(PreBasePydanticModel):
    name: str | None = None
    description: str | None = None


class CreatePlanSchema(PreBasePydanticModel):
    name: str
    description: str | None = None
    questions: list[CreateQuestionSchema] = Field(default_factory=list)


class UpdateQuestionSchema(PreBasePydanticModel):
    text: str | None = None
    type: str | None = None
    criteria: list[str] | None = None


class GetQuestionSchema(PreBasePydanticModel):
    id: int
    text: str
    type: str
    criteria: list[str]


class GetPlanSchema(PreBasePydanticModel):
    id: int
    name: str
    description: str | None
    status: str
    questions: list[GetQuestionSchema]
