from interwiews.application.auth import AuthUseCases
from interwiews.infrastructure.uow import SQLAlchemyUnitOfWork


def auth_usecase() -> AuthUseCases:
    return AuthUseCases(SQLAlchemyUnitOfWork())
