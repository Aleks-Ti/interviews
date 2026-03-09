import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import Field

from interviews.core.exceptions import AUTH_EXEPTIONS
from interviews.core.schemas import PreBasePydanticModel
from interviews.domain.user.models import User
from interviews.providers.base import AIProvider
from interviews.providers.factory import get_ai_provider
from interviews.routers.dependencies import get_current_user

ai_router = APIRouter(
    prefix="/ai",
    tags=["ai"],
)


# --- dependency ---

def get_ai_provider_dep() -> AIProvider:
    try:
        return get_ai_provider()
    except Exception:
        raise HTTPException(status_code=503, detail="AI provider is not configured")


# --- request / response schemas ---

class SuggestQuestionRequest(PreBasePydanticModel):
    context: str
    question_type: str = "technical"


class SuggestQuestionResponse(PreBasePydanticModel):
    text: str
    type: str
    criteria: list[str]


class ExpectedAnswerRequest(PreBasePydanticModel):
    question: str
    criteria: list[str]
    context: str


class ExpectedAnswerResponse(PreBasePydanticModel):
    answer: str


class GeneratePlanRequest(PreBasePydanticModel):
    prompt: str
    question_count: int = Field(10, gt=0, le=30)


class GeneratedQuestionResponse(PreBasePydanticModel):
    text: str
    type: str
    criteria: list[str]


class GeneratePlanResponse(PreBasePydanticModel):
    name: str
    description: str
    questions: list[GeneratedQuestionResponse]


# --- endpoints ---

@ai_router.post("/question/suggest", response_model=SuggestQuestionResponse)
async def suggest_question(
    data: SuggestQuestionRequest,
    ai: Annotated[AIProvider, Depends(get_ai_provider_dep)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> SuggestQuestionResponse:
    try:
        result = await ai.suggest_question(data.context, data.question_type)
        return SuggestQuestionResponse(text=result.text, type=result.type, criteria=result.criteria)
    except AUTH_EXEPTIONS:
        raise
    except Exception as err:
        logging.exception(f"AI suggest_question failed: {err}")
        raise HTTPException(status_code=502, detail="AI request failed")


@ai_router.post("/question/expected-answer", response_model=ExpectedAnswerResponse)
async def get_expected_answer(
    data: ExpectedAnswerRequest,
    ai: Annotated[AIProvider, Depends(get_ai_provider_dep)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ExpectedAnswerResponse:
    try:
        answer = await ai.get_expected_answer(data.question, data.criteria, data.context)
        return ExpectedAnswerResponse(answer=answer)
    except AUTH_EXEPTIONS:
        raise
    except Exception as err:
        logging.exception(f"AI get_expected_answer failed: {err}")
        raise HTTPException(status_code=502, detail="AI request failed")


@ai_router.post("/plan/generate", response_model=GeneratePlanResponse)
async def generate_plan(
    data: GeneratePlanRequest,
    ai: Annotated[AIProvider, Depends(get_ai_provider_dep)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> GeneratePlanResponse:
    try:
        result = await ai.generate_plan(data.prompt, data.question_count)
        return GeneratePlanResponse(
            name=result.name,
            description=result.description,
            questions=[
                GeneratedQuestionResponse(text=q.text, type=q.type, criteria=q.criteria)
                for q in result.questions
            ],
        )
    except AUTH_EXEPTIONS:
        raise
    except Exception as err:
        logging.exception(f"AI generate_plan failed: {err}")
        raise HTTPException(status_code=502, detail="AI request failed")
