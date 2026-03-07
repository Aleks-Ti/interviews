from collections.abc import Sequence
from uuid import UUID

from interwiews.common import jwt_auth
from interwiews.common.jwt_auth import get_password_hash
from interwiews.domain.user.exceptions import (
    AdminNotChangeCommentingRightsAdminAndOwner,
    AdminNotRestoreOrDeletedAnotherAdmin,
    NotAllowedEditPasswordToAdmin,
)
from interwiews.domain.user.models import RoleName, User
from interwiews.domain.user.repository import UserRepository
from interwiews.domain.user.schemas import (
    ChangePasswordUserSchema,
    CreateUserSchema,
    UserFilters,
)


class UserService:
    def __init__(
        self,
        user_repository: UserRepository,
    ) -> None:
        self.user_repository: UserRepository = user_repository

    async def get_users(self, filters: UserFilters) -> Sequence[User]:
        users = await self.user_repository.find_all_by_filter(filters)
        return users

    async def get_user(self, user_id: UUID) -> User:
        user = await self.user_repository.find_one(user_id)
        return user

    async def get_user_me(self, user: User) -> User:
        return await self.user_repository.find_one(user.id)

    async def create_user(self, user_data: CreateUserSchema) -> User:
        base_data_for_create = user_data.model_dump()
        base_data_for_create["password"] = jwt_auth.get_password_hash(base_data_for_create["password"])
        user = await self.user_repository.add_one(base_data_for_create)
        user_with_roles = await self.user_repository.find_one(user.id)

        return user_with_roles

    async def delete_user(self, user_id: UUID, current_user: User) -> User:
        target_user = await self.user_repository.find_one(user_id)
        if target_user.role.name == RoleName.admin and current_user.role.name != RoleName.admin:
            raise AdminNotRestoreOrDeletedAnotherAdmin
        return await self.user_repository.update_one(user_id, {"is_active": False})

    async def restore_user(self, user_id: UUID, current_user: User) -> User:
        target_user = await self.user_repository.find_one(user_id)
        if target_user.role.name == RoleName.admin and current_user.role.name != RoleName.admin:
            raise AdminNotRestoreOrDeletedAnotherAdmin
        return await self.user_repository.update_one(user_id, {"is_active": True})

    async def change_user_password(self, user_id: UUID, new_password) -> None:
        cache_password = get_password_hash(new_password)
        new_data = {"password": cache_password}
        await self.user_repository.update_one(user_id, new_data)

    async def edit_password(self, data: ChangePasswordUserSchema, current_user: User) -> User:
        target_user = await self.user_repository.find_one(data.user_id)
        if target_user.role.name == RoleName.admin and current_user.role.name != RoleName.admin:
            raise NotAllowedEditPasswordToAdmin
        new_password = jwt_auth.get_password_hash(data.password)
        user = await self.user_repository.update_one(target_user.id, {"password": new_password})
        return user

    async def change_user_is_allowed_comment(self, user_id: UUID, current_user: User, is_allowed_comment: bool):
        target_user = await self.user_repository.find_one(user_id)
        if target_user.role.name in (RoleName.admin, RoleName.owner) and current_user.role.name != RoleName.admin:
            raise AdminNotChangeCommentingRightsAdminAndOwner
        data = {"is_allowed_comment": is_allowed_comment}
        return await self.user_repository.update_one(user_id, data)
