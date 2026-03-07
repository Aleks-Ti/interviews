from interwiews.application.user import UserUseCases
from interwiews.infrastructure.uow import SQLAlchemyUnitOfWork


def user_usecase() -> UserUseCases:
    return UserUseCases(SQLAlchemyUnitOfWork())
