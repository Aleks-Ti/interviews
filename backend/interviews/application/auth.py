from fastapi import Response

from interviews.application.uow import AbstractUnitOfWork
from interviews.domain.auth.schemas import LoginUserSchema
from interviews.domain.auth.service import AuthService


class AuthUseCases:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self.uow = uow

    async def login(self, data: LoginUserSchema):
        async with self.uow as uow:
            service = AuthService(uow.auth_users)
            return await service.authenticate_user(data)

    async def logout(self, response: Response) -> None:
        async with self.uow as uow:
            service = AuthService(uow.auth_users)
            return await service.logout_user(response)
