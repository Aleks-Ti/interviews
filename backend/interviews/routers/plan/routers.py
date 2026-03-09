import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from interviews.application.plan import PlanUseCases
from interviews.core.exceptions import AUTH_EXEPTIONS
from interviews.domain.plan.exceptions import PlanNotEditable, PlanNotFound, QuestionNotFound
from interviews.domain.plan.models import Plan, Question
from interviews.domain.plan.schemas import (
    CreatePlanSchema,
    CreateQuestionSchema,
    GetPlanSchema,
    GetQuestionSchema,
    PlanFilters,
    UpdatePlanSchema,
    UpdateQuestionSchema,
)
from interviews.domain.user.models import User
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
        return await plan_usecase.get_plans(current_user.id, query_params)
    except AUTH_EXEPTIONS:
        raise
    except Exception as err:
        logging.exception(f"Error getting list of plans. Error: {err}")
        raise HTTPException(status_code=400, detail="Error getting list of plans")


@plan_router.get("/{plan_id}", response_model=GetPlanSchema)
async def get_plan(
    plan_id: int,
    plan_usecase: Annotated[PlanUseCases, Depends(_plan_usecase)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Plan:
    try:
        return await plan_usecase.get_plan(plan_id, current_user.id)
    except PlanNotFound:
        raise HTTPException(status_code=404, detail="Plan not found")
    except AUTH_EXEPTIONS:
        raise
    except Exception as err:
        logging.exception(f"Error getting plan {plan_id}. Error: {err}")
        raise HTTPException(status_code=400, detail="Error getting plan")


@plan_router.post("", response_model=GetPlanSchema, status_code=201)
async def create_plan(
    data: CreatePlanSchema,
    plan_usecase: Annotated[PlanUseCases, Depends(_plan_usecase)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Plan:
    try:
        return await plan_usecase.create_plan(data, current_user.id)
    except AUTH_EXEPTIONS:
        raise
    except Exception as err:
        logging.exception(f"Error creating plan. Error: {err}")
        raise HTTPException(status_code=400, detail="Error creating plan")


@plan_router.patch("/{plan_id}", response_model=GetPlanSchema)
async def update_plan(
    plan_id: int,
    data: UpdatePlanSchema,
    plan_usecase: Annotated[PlanUseCases, Depends(_plan_usecase)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Plan:
    try:
        return await plan_usecase.update_plan(plan_id, data, current_user.id)
    except PlanNotFound:
        raise HTTPException(status_code=404, detail="Plan not found")
    except PlanNotEditable:
        raise HTTPException(status_code=409, detail="Plan is published and cannot be edited. Fork it to make changes.")
    except AUTH_EXEPTIONS:
        raise
    except Exception as err:
        logging.exception(f"Error updating plan {plan_id}. Error: {err}")
        raise HTTPException(status_code=400, detail="Error updating plan")


@plan_router.delete("/{plan_id}", status_code=204)
async def delete_plan(
    plan_id: int,
    plan_usecase: Annotated[PlanUseCases, Depends(_plan_usecase)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    try:
        await plan_usecase.delete_plan(plan_id, current_user.id)
    except PlanNotFound:
        raise HTTPException(status_code=404, detail="Plan not found")
    except AUTH_EXEPTIONS:
        raise
    except Exception as err:
        logging.exception(f"Error deleting plan {plan_id}. Error: {err}")
        raise HTTPException(status_code=400, detail="Error deleting plan")


@plan_router.post("/{plan_id}/fork", response_model=GetPlanSchema, status_code=201)
async def fork_plan(
    plan_id: int,
    plan_usecase: Annotated[PlanUseCases, Depends(_plan_usecase)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Plan:
    try:
        return await plan_usecase.fork_plan(plan_id, current_user.id)
    except PlanNotFound:
        raise HTTPException(status_code=404, detail="Plan not found")
    except AUTH_EXEPTIONS:
        raise
    except Exception as err:
        logging.exception(f"Error forking plan {plan_id}. Error: {err}")
        raise HTTPException(status_code=400, detail="Error forking plan")


@plan_router.post("/{plan_id}/publish", response_model=GetPlanSchema)
async def publish_plan(
    plan_id: int,
    plan_usecase: Annotated[PlanUseCases, Depends(_plan_usecase)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Plan:
    try:
        return await plan_usecase.publish_plan(plan_id, current_user.id)
    except PlanNotFound:
        raise HTTPException(status_code=404, detail="Plan not found")
    except AUTH_EXEPTIONS:
        raise
    except Exception as err:
        logging.exception(f"Error publishing plan {plan_id}. Error: {err}")
        raise HTTPException(status_code=400, detail="Error publishing plan")


# --- Questions ---

@plan_router.post("/{plan_id}/questions", response_model=GetQuestionSchema, status_code=201)
async def add_question(
    plan_id: int,
    data: CreateQuestionSchema,
    plan_usecase: Annotated[PlanUseCases, Depends(_plan_usecase)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Question:
    try:
        return await plan_usecase.add_question(plan_id, data, current_user.id)
    except PlanNotFound:
        raise HTTPException(status_code=404, detail="Plan not found")
    except PlanNotEditable:
        raise HTTPException(status_code=409, detail="Plan is published and cannot be edited. Fork it to make changes.")
    except AUTH_EXEPTIONS:
        raise
    except Exception as err:
        logging.exception(f"Error adding question to plan {plan_id}. Error: {err}")
        raise HTTPException(status_code=400, detail="Error adding question")


@plan_router.patch("/{plan_id}/questions/{question_id}", response_model=GetQuestionSchema)
async def update_question(
    plan_id: int,
    question_id: int,
    data: UpdateQuestionSchema,
    plan_usecase: Annotated[PlanUseCases, Depends(_plan_usecase)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Question:
    try:
        return await plan_usecase.update_question(plan_id, question_id, data, current_user.id)
    except PlanNotFound:
        raise HTTPException(status_code=404, detail="Plan not found")
    except PlanNotEditable:
        raise HTTPException(status_code=409, detail="Plan is published and cannot be edited. Fork it to make changes.")
    except QuestionNotFound:
        raise HTTPException(status_code=404, detail="Question not found")
    except AUTH_EXEPTIONS:
        raise
    except Exception as err:
        logging.exception(f"Error updating question {question_id}. Error: {err}")
        raise HTTPException(status_code=400, detail="Error updating question")


@plan_router.delete("/{plan_id}/questions/{question_id}", status_code=204)
async def delete_question(
    plan_id: int,
    question_id: int,
    plan_usecase: Annotated[PlanUseCases, Depends(_plan_usecase)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    try:
        await plan_usecase.delete_question(plan_id, question_id, current_user.id)
    except PlanNotFound:
        raise HTTPException(status_code=404, detail="Plan not found")
    except PlanNotEditable:
        raise HTTPException(status_code=409, detail="Plan is published and cannot be edited. Fork it to make changes.")
    except QuestionNotFound:
        raise HTTPException(status_code=404, detail="Question not found")
    except AUTH_EXEPTIONS:
        raise
    except Exception as err:
        logging.exception(f"Error deleting question {question_id}. Error: {err}")
        raise HTTPException(status_code=400, detail="Error deleting question")
