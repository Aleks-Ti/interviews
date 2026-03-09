from interviews.core.schemas import PreBasePydanticModel


class GetAnalysisSchema(PreBasePydanticModel):
    id: int
    score: float
    summary: str
    strengths: list[str]
    weaknesses: list[str]
    recommendation: str
    answer_id: int
