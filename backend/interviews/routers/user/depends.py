from interviews.application.user import UserUseCases
from interviews.infrastructure.uow import SQLAlchemyUnitOfWork


def user_usecase() -> UserUseCases:
    return UserUseCases(SQLAlchemyUnitOfWork())
