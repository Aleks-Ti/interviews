import logging
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import Field
from sqlalchemy.ext.asyncio import AsyncSession

from interviews.core.exceptions import AUTH_EXEPTIONS
from interviews.core.schemas import PreBasePydanticModel
from interviews.domain.user.models import User
from interviews.infrastructure.database.connection import get_async_session
from interviews.infrastructure.repository.persistence.question import PostgresQuestionRepository
from interviews.providers.base import AIProvider
from interviews.providers.factory import get_ai_provider
from interviews.providers.whisper import LocalWhisper, get_local_whisper
from interviews.routers.dependencies import get_current_user

ai_router = APIRouter(
    prefix="/ai",
    tags=["ai"],
)


def get_ai_provider_dep() -> AIProvider:
    try:
        return get_ai_provider()
    except Exception:
        raise HTTPException(status_code=503, detail="AI provider is not configured")


# --- schemas ---

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
    question_id: int | None = None


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

class TranscribeResponse(PreBasePydanticModel):
    transcript: str


@ai_router.post("/transcribe", response_model=TranscribeResponse)
async def transcribe_audio(
    file: Annotated[UploadFile, File(...)],
    current_user: Annotated[User, Depends(get_current_user)],
    whisper: Annotated[LocalWhisper, Depends(get_local_whisper)],
) -> TranscribeResponse:
    """
    Транскрибировать аудиофайл без сохранения в БД.

    Используется для предварительной транскрипции перед сохранением ответа.
    Транскрибация выполняется локально через openai-whisper (ключ API не требуется).
    """
    try:
        audio = await file.read()
        transcript = await whisper.transcribe(audio, file.filename or "audio.webm")
        return TranscribeResponse(transcript=transcript)
    except AUTH_EXEPTIONS:
        raise
    except Exception as err:
        logging.exception(f"Transcription failed: {err}")
        raise HTTPException(status_code=502, detail="Transcription failed")


@ai_router.post("/question/suggest", response_model=SuggestQuestionResponse)
async def suggest_question(
    data: SuggestQuestionRequest,
    ai: Annotated[AIProvider, Depends(get_ai_provider_dep)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> SuggestQuestionResponse:
    """
    Сгенерировать вопрос с помощью AI.

    AI составляет один профессиональный вопрос под заданный контекст
    (роль, технологии, уровень) и тип (<code>technical</code> / <code>behavioral</code> / <code>custom</code>).
    Возвращает текст вопроса, тип и критерии оценки — готово для сохранения
    через <code>POST /plan/{id}/questions</code>.
    """
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
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> ExpectedAnswerResponse:
    """
    Получить ожидаемый ответ на вопрос.

    AI генерирует эталонный ответ на вопрос интервью — помогает интервьюеру,
    который не разбирается в теме, понять что должен был ответить кандидат
    и оценить полноту ответа. Если передан <code>question_id</code>, ответ
    сохраняется в вопрос и при следующем запросе возвращается без обращения к AI.
    """
    try:
        answer = await ai.get_expected_answer(data.question, data.criteria, data.context)
        if data.question_id is not None:
            repo = PostgresQuestionRepository(session)
            await repo.update_one(data.question_id, {"expected_answer": answer})
            await session.commit()
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
    """
    Сгенерировать план интервью с помощью AI.

    AI составляет полный план на основе свободного описания:
    роль, уровень, стек, акцент. Возвращает название, описание и список
    вопросов с критериями — <b>план не сохраняется автоматически</b>.
    Клиент может отредактировать результат и сохранить через
    <code>POST /plan</code>.

    <b>Пример запроса:</b>
    <code>{"prompt": "стажёр Python, веб-отдел, уклон в сети", "question_count": 8}</code>
    """
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
