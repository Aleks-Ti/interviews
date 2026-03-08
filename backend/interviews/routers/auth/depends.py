from interviews.application.auth import AuthUseCases
from interviews.infrastructure.uow import SQLAlchemyUnitOfWork


def auth_usecase() -> AuthUseCases:
    return AuthUseCases(SQLAlchemyUnitOfWork())
