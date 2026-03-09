from fastapi import APIRouter

from interviews.routers.ai.routers import ai_router
from interviews.routers.auth.routers import auth_router
from interviews.routers.interview.routers import interview_router
from interviews.routers.plan.plan_routers import plan_router
from interviews.routers.plan.question_routers import question_router
from interviews.routers.user.routers import user_router

api = APIRouter(
    prefix="/api",
    responses={404: {"description": "Page not found"}},
)

api.include_router(user_router)
api.include_router(auth_router)
api.include_router(plan_router)
api.include_router(question_router)
api.include_router(interview_router)
api.include_router(ai_router)
