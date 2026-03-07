from fastapi import APIRouter

from interwiews.routers.auth.routers import auth_router
from interwiews.routers.user.routers import user_router

api = APIRouter(
    prefix="/api",
    responses={404: {"description": "Page not found"}},
)

api.include_router(user_router)
api.include_router(auth_router)
