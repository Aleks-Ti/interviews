import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from interviews.application.plan import PlanUseCases
from interviews.core.exceptions import AUTH_EXEPTIONS
from interviews.domain.plan.exceptions import PlanNotEditable, PlanNotFound, QuestionNotFound
from interviews.domain.plan.models import Question
from interviews.domain.plan.schemas import CreateQuestionSchema, GetQuestionSchema, UpdateQuestionSchema
from interviews.domain.user.models import User
from interviews.routers.dependencies import get_current_user
from interviews.routers.plan.depends import plan_usecase as _plan_usecase

question_router = APIRouter(
    prefix="/plan/{plan_id}/questions",
    tags=["questions"],
    responses={404: {"description": "Page not found"}},
)


@question_router.post("", response_model=GetQuestionSchema, status_code=201)
async def add_question(
    plan_id: int,
    data: CreateQuestionSchema,
    plan_usecase: Annotated[PlanUseCases, Depends(_plan_usecase)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Question:
    """
    Добавить вопрос в план.

    Доступно только для планов в статусе <code>draft</code>.
    Тип вопроса: <code>technical</code>, <code>behavioral</code>, <code>custom</code>.
    """
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


@question_router.patch("/{question_id}", response_model=GetQuestionSchema)
async def update_question(
    plan_id: int,
    question_id: int,
    data: UpdateQuestionSchema,
    plan_usecase: Annotated[PlanUseCases, Depends(_plan_usecase)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Question:
    """
    Обновить вопрос.

    Можно изменить текст, тип или критерии оценки.
    Доступно только для планов в статусе <code>draft</code>.
    """
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


@question_router.delete("/{question_id}", status_code=204)
async def delete_question(
    plan_id: int,
    question_id: int,
    plan_usecase: Annotated[PlanUseCases, Depends(_plan_usecase)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    """
    Удалить вопрос из плана.

    Каскадно удаляет связанные ответы и их анализ.
    Доступно только для планов в статусе <code>draft</code>.
    """
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
