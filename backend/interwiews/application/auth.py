from fastapi import Response

from interwiews.application.uow import AbstractUnitOfWork
from interwiews.domain.auth.schemas import LoginUserSchema
from interwiews.domain.auth.service import AuthService


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
