import logging
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import HTTPException, Security
from fastapi.params import Depends
from fastapi.security import APIKeyCookie
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from interwiews.common.configuration import conf
from interwiews.common.exceptions import (
    InvalidTokenException,
    UserNotActiveException,
    UserNotAuthorizedException,
    UserRoleNotMatchedException,
)
from interwiews.domain.user.models import RoleName, User
from interwiews.domain.user.repository import UserRepository
from interwiews.infrastructure.database.connection import get_async_session
from interwiews.infrastructure.repository.persistence.user import PostgresUserRepository

auth_scheme = APIKeyCookie(name="authorization", auto_error=False)


def get_user_repository(session: AsyncSession = Depends(get_async_session)) -> UserRepository:
    return PostgresUserRepository(session)


async def get_current_user(
    token_in_cookie: str = Security(auth_scheme),
    user_repository: UserRepository = Depends(get_user_repository),
) -> User:
    try:
        if not token_in_cookie:
            raise UserNotAuthorizedException
        payload = jwt.decode(token_in_cookie, conf.token.secret_key, algorithms=[conf.token.jwt_sign_algorithm])
        user_id: UUID | None = payload.get("sub")
        exp_time_value = payload.get("exp")

        if user_id is None or exp_time_value is None:
            raise JWTError
        if datetime.fromtimestamp(float(exp_time_value), tz=UTC) < datetime.now(UTC):
            raise JWTError

        user = await user_repository.find_one_or_none(user_id)
        if user is None:
            raise InvalidTokenException
        if not user.is_active:
            raise UserNotActiveException
        return user
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid token.")
    except (UserNotActiveException, InvalidTokenException, UserNotAuthorizedException):
        raise
    except Exception:
        logging.exception("Error getting authorization data")
        raise HTTPException(status_code=400, detail="Error getting authorization data.")


def role_required(required_roles: list[RoleName]) -> Callable:
    async def role_check(current_user: Annotated[User, Depends(get_current_user)]) -> User:
        if current_user.role.name not in required_roles:
            raise UserRoleNotMatchedException
        return current_user

    return role_check
