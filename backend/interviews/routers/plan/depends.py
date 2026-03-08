from interviews.application.plan import PlanUseCases
from interviews.infrastructure.uow import SQLAlchemyUnitOfWork


def plan_usecase() -> PlanUseCases:
    return PlanUseCases(SQLAlchemyUnitOfWork())
