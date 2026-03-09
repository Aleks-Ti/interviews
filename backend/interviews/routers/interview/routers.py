import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from interviews.application.interview import InterviewUseCases
from interviews.core.exceptions import AUTH_EXEPTIONS
from interviews.domain.interview.exceptions import InterviewInvalidStatus, InterviewNotFound
from interviews.domain.interview.models import Answer, Interview
from interviews.domain.interview.schemas import (
    GetAnswerSchema,
    GetInterviewSchema,
    InterviewFilters,
    StartInterviewSchema,
    SubmitAnswerSchema,
)
from interviews.domain.plan.exceptions import PlanNotFound
from interviews.domain.user.models import User
from interviews.routers.dependencies import get_current_user
from interviews.routers.interview.depends import interview_usecase as _interview_usecase

interview_router = APIRouter(
    prefix="/interview",
    tags=["interview"],
    responses={404: {"description": "Page not found"}},
)


@interview_router.get("", response_model=list[GetInterviewSchema])
async def get_interviews(
    query_params: Annotated[InterviewFilters, Query()],
    interview_usecase: Annotated[InterviewUseCases, Depends(_interview_usecase)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[Interview]:
    try:
        return await interview_usecase.get_interviews(current_user.id, query_params)
    except AUTH_EXEPTIONS:
        raise
    except Exception as err:
        logging.exception(f"Error getting interviews. Error: {err}")
        raise HTTPException(status_code=400, detail="Error getting interviews")


@interview_router.get("/{interview_id}", response_model=GetInterviewSchema)
async def get_interview(
    interview_id: int,
    interview_usecase: Annotated[InterviewUseCases, Depends(_interview_usecase)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Interview:
    try:
        return await interview_usecase.get_interview(interview_id, current_user.id)
    except InterviewNotFound:
        raise HTTPException(status_code=404, detail="Interview not found")
    except AUTH_EXEPTIONS:
        raise
    except Exception as err:
        logging.exception(f"Error getting interview {interview_id}. Error: {err}")
        raise HTTPException(status_code=400, detail="Error getting interview")


@interview_router.post("", response_model=GetInterviewSchema, status_code=201)
async def start_interview(
    data: StartInterviewSchema,
    interview_usecase: Annotated[InterviewUseCases, Depends(_interview_usecase)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Interview:
    try:
        return await interview_usecase.start_interview(data, current_user.id)
    except PlanNotFound:
        raise HTTPException(status_code=404, detail="Plan not found")
    except AUTH_EXEPTIONS:
        raise
    except Exception as err:
        logging.exception(f"Error starting interview. Error: {err}")
        raise HTTPException(status_code=400, detail="Error starting interview")


@interview_router.post("/{interview_id}/begin", response_model=GetInterviewSchema)
async def begin_interview(
    interview_id: int,
    interview_usecase: Annotated[InterviewUseCases, Depends(_interview_usecase)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Interview:
    try:
        return await interview_usecase.begin_interview(interview_id, current_user.id)
    except InterviewNotFound:
        raise HTTPException(status_code=404, detail="Interview not found")
    except InterviewInvalidStatus:
        raise HTTPException(status_code=409, detail="Interview must be in 'pending' status to begin")
    except AUTH_EXEPTIONS:
        raise
    except Exception as err:
        logging.exception(f"Error beginning interview {interview_id}. Error: {err}")
        raise HTTPException(status_code=400, detail="Error beginning interview")


@interview_router.post("/{interview_id}/complete", response_model=GetInterviewSchema)
async def complete_interview(
    interview_id: int,
    interview_usecase: Annotated[InterviewUseCases, Depends(_interview_usecase)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Interview:
    try:
        return await interview_usecase.complete_interview(interview_id, current_user.id)
    except InterviewNotFound:
        raise HTTPException(status_code=404, detail="Interview not found")
    except InterviewInvalidStatus:
        raise HTTPException(status_code=409, detail="Interview must be in 'in_progress' status to complete")
    except AUTH_EXEPTIONS:
        raise
    except Exception as err:
        logging.exception(f"Error completing interview {interview_id}. Error: {err}")
        raise HTTPException(status_code=400, detail="Error completing interview")


@interview_router.delete("/{interview_id}", status_code=204)
async def delete_interview(
    interview_id: int,
    interview_usecase: Annotated[InterviewUseCases, Depends(_interview_usecase)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    try:
        await interview_usecase.delete_interview(interview_id, current_user.id)
    except InterviewNotFound:
        raise HTTPException(status_code=404, detail="Interview not found")
    except AUTH_EXEPTIONS:
        raise
    except Exception as err:
        logging.exception(f"Error deleting interview {interview_id}. Error: {err}")
        raise HTTPException(status_code=400, detail="Error deleting interview")


@interview_router.post("/{interview_id}/answers", response_model=GetAnswerSchema, status_code=201)
async def submit_answer(
    interview_id: int,
    data: SubmitAnswerSchema,
    interview_usecase: Annotated[InterviewUseCases, Depends(_interview_usecase)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Answer:
    try:
        return await interview_usecase.submit_answer(interview_id, data, current_user.id)
    except InterviewNotFound:
        raise HTTPException(status_code=404, detail="Interview not found")
    except InterviewInvalidStatus:
        raise HTTPException(status_code=409, detail="Interview must be in 'in_progress' status to submit answers")
    except AUTH_EXEPTIONS:
        raise
    except Exception as err:
        logging.exception(f"Error submitting answer for interview {interview_id}. Error: {err}")
        raise HTTPException(status_code=400, detail="Error submitting answer")
