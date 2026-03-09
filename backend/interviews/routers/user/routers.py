import logging
from _collections_abc import Sequence
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import NoResultFound

from interviews.application.user import UserUseCases
from interviews.core.exceptions import AUTH_EXEPTIONS, NoContent, UserAlreadyExistsException
from interviews.domain.user.exceptions import (
    AdminNotRestoreOrDeletedAnotherAdmin,
    NotAllowedEditPasswordToAdmin,
)
from interviews.domain.user.models import RoleName, User
from interviews.domain.user.schemas import (
    ChangePasswordUserSchema,
    CreateUserSchema,
    GetUserSchema,
    UserFilters,
)
from interviews.routers.dependencies import get_current_user, role_required
from interviews.routers.user.depends import user_usecase as _user_usecase

user_router = APIRouter(
    prefix="/user",
    tags=["user"],
    responses={404: {"description": "Page not found"}},
)


@user_router.get("", response_model=list[GetUserSchema], dependencies=[Depends(role_required([RoleName.admin]))])
async def get_users(
    query_params: Annotated[UserFilters, Query()],
    user_usecase: Annotated[UserUseCases, Depends(_user_usecase)],
) -> Sequence[User]:
    try:
        users = await user_usecase.get_users(query_params)
        return users
    except AUTH_EXEPTIONS:
        raise
    except Exception as err:
        logging.exception(f"Error getting list of users. Error: {err}")
        raise HTTPException(status_code=400, detail="Error getting list of users")


@user_router.post(
    "/create",
    response_model=GetUserSchema,
)
async def create_user(user_data: CreateUserSchema, auth_usecase: Annotated[UserUseCases, Depends(_user_usecase)]) -> User:
    try:
        user = await auth_usecase.create_user(user_data)
        return user
    except UserAlreadyExistsException:
        raise
    except AUTH_EXEPTIONS:
        raise
    except Exception as err:
        logging.exception(f"User registration error. Username: {user_data.email} Error: {err}")
        raise HTTPException(status_code=400, detail="User registration error")


@user_router.get("/me", response_model=GetUserSchema)
async def get_user_me(
    user_usecase: Annotated[UserUseCases, Depends(_user_usecase)], auth_user: Annotated[User, Depends(get_current_user)]
) -> User:
    try:
        user = await user_usecase.get_user_me(auth_user)
        return user
    except AUTH_EXEPTIONS:
        raise
    except NoContent:
        raise
    except Exception as err:
        logging.exception(f"Error getting a user. Error: {err}")
        raise HTTPException(status_code=400, detail="Error getting a user")


@user_router.post("/change-password", response_model=dict)
async def change_password_user(
    user_data: ChangePasswordUserSchema,
    user_usecase: Annotated[UserUseCases, Depends(_user_usecase)],
    auth_user: Annotated[User, Depends(get_current_user)],
) -> dict:
    try:
        message = await user_usecase.edit_password_user(user_data, auth_user)
        return message
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Not found item.")
    except NotAllowedEditPasswordToAdmin:
        raise HTTPException(status_code=403, detail="Нельзя менять пароли для администратора.")
    except Exception as err:
        logging.exception(f"Error changing a user. User_id: {user_data.user_id} Error: {err}")
        raise HTTPException(status_code=400, detail="Error changing a user")


@user_router.get("/{user_id}", response_model=GetUserSchema, dependencies=[Depends(role_required([RoleName.admin]))])
async def get_user(
    user_id: UUID,
    user_usecase: Annotated[UserUseCases, Depends(_user_usecase)],
) -> User:
    try:
        user = await user_usecase.get_user(user_id)
        return user
    except AUTH_EXEPTIONS:
        raise
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Not found item.")
    except Exception as err:
        logging.exception(f"Error getting a user. Error: {err}")
        raise HTTPException(status_code=400, detail="Error getting a user")


@user_router.delete("/delete-user/{user_id}", response_model=GetUserSchema)
async def delete_user(
    user_id: UUID,
    user_usecase: Annotated[UserUseCases, Depends(_user_usecase)],
    auth_user: Annotated[User, Depends(role_required([RoleName.admin]))],
) -> User:
    try:
        user = await user_usecase.delete_user(user_id, auth_user)
        return user
    except AUTH_EXEPTIONS:
        raise
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Not found item.")
    except AdminNotRestoreOrDeletedAnotherAdmin:
        raise HTTPException(status_code=403, detail="Администратор не может забанить или разбанить другого администратора.")
    except Exception as err:
        logging.exception(f"Error delete user. User_id: {user_id} Error: {err}")
        raise HTTPException(status_code=400, detail="Error delete user")


@user_router.post("/restore-user/{user_id}", response_model=GetUserSchema)
async def restore_user(
    user_id: UUID,
    user_usecase: Annotated[UserUseCases, Depends(_user_usecase)],
    auth_user: Annotated[User, Depends(role_required([RoleName.admin]))],
) -> User:
    try:
        user = await user_usecase.restore_user(user_id, auth_user)
        return user
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Not found item.")
    except AdminNotRestoreOrDeletedAnotherAdmin:
        raise HTTPException(status_code=403, detail="Администратор не может забанить или разбанить другого администратора.")
    except Exception as err:
        logging.exception(f"Error restore user. User_id: {user_id} Error: {err}")
        raise HTTPException(status_code=400, detail="Error restore user")
