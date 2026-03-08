from interviews.core.schemas import PreBasePydanticModel


class StartInterviewSchema(PreBasePydanticModel):
    plan_id: int
