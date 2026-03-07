from collections.abc import Sequence
from uuid import UUID

from interwiews.application.uow import AbstractUnitOfWork
from interwiews.domain.user.models import User
from interwiews.domain.user.schemas import ChangePasswordUserSchema, CreateUserSchema, UserFilters
from interwiews.domain.user.service import UserService


class UserUseCases:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self.uow = uow

    async def get_users(self, filters: UserFilters) -> Sequence[User]:
        async with self.uow as uow:
            service = UserService(uow.users)
            return await service.get_users(filters)

    async def get_user(self, user_id: UUID) -> User:
        async with self.uow as uow:
            service = UserService(uow.users)
            return await service.get_user(user_id)

    async def delete_user(self, user_id: UUID, current_user: User) -> User:
        async with self.uow as uow:
            service = UserService(uow.users)
            user = await service.delete_user(user_id, current_user)
            await uow.commit()
            return user

    async def restore_user(self, user_id: UUID, current_user: User) -> User:
        async with self.uow as uow:
            service = UserService(uow.users)
            user = await service.restore_user(user_id, current_user)
            await uow.commit()
            return user

    async def get_user_me(self, current_user: User) -> User:
        async with self.uow as uow:
            service = UserService(uow.users)
            return await service.get_user_me(current_user)

    async def create_user(self, create_user_data: CreateUserSchema) -> User:
        async with self.uow as uow:
            service = UserService(uow.users)
            user = await service.create_user(create_user_data)
            await uow.commit()
            return user

    async def edit_password_user(self, data: ChangePasswordUserSchema, current_user: User) -> dict:
        async with self.uow as uow:
            service = UserService(uow.users)
            await service.edit_password(data, current_user)
            await uow.commit()
        return {"message": "password change was completed successfully"}

    async def change_user_is_allowed_comment(self, user_id: UUID, current_user: User, is_allowed_comment: bool):
        async with self.uow as uow:
            service = UserService(uow.users)
            user = await service.change_user_is_allowed_comment(user_id, current_user, is_allowed_comment)
            await uow.commit()
            return user
