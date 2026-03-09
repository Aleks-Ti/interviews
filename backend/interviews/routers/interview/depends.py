from interviews.application.interview import InterviewUseCases
from interviews.infrastructure.uow import SQLAlchemyUnitOfWork
from interviews.providers.factory import get_ai_provider


def interview_usecase() -> InterviewUseCases:
    try:
        ai = get_ai_provider()
    except Exception:
        ai = None
    return InterviewUseCases(SQLAlchemyUnitOfWork(), ai)
