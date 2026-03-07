from datetime import UTC, datetime, timedelta

from fastapi import Response
from fastapi.responses import JSONResponse

from interwiews.core import jwt_auth
from interwiews.core.exceptions import UserCredentialsException
from interwiews.domain.auth.models import User
from interwiews.domain.auth.repository import AuthUserRepository
from interwiews.domain.auth.schemas import LoginUserSchema


class AuthService:
    def __init__(self, user_repository: AuthUserRepository) -> None:
        self.user_repository = user_repository

    async def authenticate_user(self, user_data: LoginUserSchema) -> JSONResponse:
        user: User | None = await self.user_repository.find_by_email(user_data.email)
        if not user:
            raise UserCredentialsException
        check_pass = jwt_auth.verify_password(user_data.password, user.password)
        if not user or not check_pass:
            raise UserCredentialsException
        access_token = jwt_auth.create_access_token(str(user.id))
        response = JSONResponse({"message": "Login successful"})
        response.set_cookie(
            key="authorization",
            value=access_token,
            httponly=True,
            expires=datetime.now(UTC) + timedelta(minutes=jwt_auth.conf.token.access_token_expire_minutes),
            path="/",
            secure=True,  # Set it to True if you're using HTTPS
            samesite="lax",
        )
        return response

    async def logout_user(self, response: Response) -> None:
        return response.delete_cookie("authorization")
