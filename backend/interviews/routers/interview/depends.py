from interviews.application.interview import InterviewUseCases
from interviews.infrastructure.uow import SQLAlchemyUnitOfWork


def interview_usecase() -> InterviewUseCases:
    return InterviewUseCases(SQLAlchemyUnitOfWork())
