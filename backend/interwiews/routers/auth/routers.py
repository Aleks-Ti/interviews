import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import JSONResponse

from interwiews.application.auth import AuthUseCases
from interwiews.common.exceptions import AUTH_EXEPTIONS, UserCredentialsException, UserNotActiveException
from interwiews.domain.auth.schemas import LoginUserSchema, LogoutSuccessSchema
from interwiews.routers.auth.depends import auth_usecase as _auth_usecase
from interwiews.routers.dependencies import get_current_user

auth_router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={404: {"description": "Page not found"}},
)


@auth_router.post(
    "/login",
)
async def login_for_token(
    user_data: LoginUserSchema,
    auth_usecase: Annotated[AuthUseCases, Depends(_auth_usecase)],
) -> JSONResponse:
    try:
        access_token = await auth_usecase.login(user_data)
        return access_token
    except (UserCredentialsException, UserNotActiveException):
        raise
    except Exception as err:
        logging.exception(f"Error user auth (error create token). Username: {user_data.email} Error: {err}")
        raise HTTPException(status_code=400, detail="User authorization error")


@auth_router.get(
    "/logout",
    response_model=LogoutSuccessSchema,
    dependencies=[Depends(get_current_user)],
)
async def logout(
    response: Response,
    auth_usecase: Annotated[AuthUseCases, Depends(_auth_usecase)],
) -> dict[str, str]:
    try:
        await auth_usecase.logout(response)
        return {"message": "Logout successful"}
    except AUTH_EXEPTIONS:
        raise
    except Exception as err:
        logging.exception(f"Logout error. Error: {err}")
        raise HTTPException(status_code=400, detail="Logout error")
