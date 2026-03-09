from fastapi import APIRouter

from interviews.routers.auth.routers import auth_router
from interviews.routers.interview.routers import interview_router
from interviews.routers.plan.routers import plan_router
from interviews.routers.user.routers import user_router

api = APIRouter(
    prefix="/api",
    responses={404: {"description": "Page not found"}},
)

api.include_router(user_router)
api.include_router(auth_router)
api.include_router(plan_router)
api.include_router(interview_router)
