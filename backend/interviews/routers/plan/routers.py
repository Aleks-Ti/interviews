import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from interviews.application.plan import PlanUseCases
from interviews.domain.plan.repository import Plan

from interviews.core.exceptions import AUTH_EXEPTIONS
from interviews.domain.plan.models import User
from interviews.domain.plan.schemas import (
    GetPlanSchema,
    PlanFilters,
)
from interviews.routers.dependencies import get_current_user
from interviews.routers.plan.depends import plan_usecase as _plan_usecase

plan_router = APIRouter(
    prefix="/plan",
    tags=["plan"],
    responses={404: {"description": "Page not found"}},
)


@plan_router.get("", response_model=list[GetPlanSchema])
async def get_plans(
    query_params: Annotated[PlanFilters, Query()],
    plan_usecase: Annotated[PlanUseCases, Depends(_plan_usecase)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[Plan]:
    try:
        plans = await plan_usecase.get_plans(current_user, query_params)
        return plans
    except AUTH_EXEPTIONS:
        raise
    except Exception as err:
        logging.exception(f"Error getting list of plans. Error: {err}")
        raise HTTPException(status_code=400, detail="Error getting list of plans")
