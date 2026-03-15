import logging
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from pydantic import BaseModel

from interviews.application.interview import InterviewUseCases
from interviews.core.exceptions import AUTH_EXEPTIONS
from interviews.domain.analysis.exceptions import AnalysisAlreadyExists, AnswerNotFound
from interviews.domain.analysis.models import Analysis
from interviews.domain.analysis.schemas import GetAnalysisSchema
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
from interviews.utils.file_handler import handle_file_upload


class AudioUploadResponse(BaseModel):
    audio_path: str

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
    """
    Получить список интервью текущего пользователя.

    Возвращает все интервью, которые проводил текущий пользователь,
    с пагинацией. Каждое интервью включает список поданных ответов.
    """
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
    """
    Получить интервью по ID.

    Возвращает детальную информацию об интервью вместе со всеми ответами кандидата.
    Доступно только создателю интервью.
    """
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
    """
    Создать новое интервью по плану.

    Создаёт интервью со статусом <code>pending</code>. Если план находился
    в статусе <code>draft</code> — он автоматически публикуется (<code>published</code>),
    после чего вопросы плана становятся неизменяемыми.

    <b>Жизненный цикл:</b> <code>pending → in_progress → completed</code>
    """
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
    """
    Начать интервью.

    Переводит интервью из <code>pending</code> в <code>in_progress</code>.
    Только в статусе <code>in_progress</code> можно подавать ответы кандидата.
    """
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
    """
    Завершить интервью.

    Переводит интервью из <code>in_progress</code> в <code>completed</code>.
    После завершения можно запустить анализ всех ответов через
    <code>POST /interview/{id}/analyze</code>.
    """
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
    """
    Удалить интервью.

    Каскадно удаляет все ответы и анализ к ним.
    """
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
    """
    Записать ответ кандидата на вопрос.

    Интервью должно быть в статусе <code>in_progress</code>.
    Можно передать текстовый транскрипт и/или путь к аудио-файлу.
    """
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


@interview_router.post("/{interview_id}/audio/{question_id}", response_model=AudioUploadResponse)
async def upload_audio(
    interview_id: int,
    question_id: int,
    file: Annotated[UploadFile, File(...)],
    interview_usecase: Annotated[InterviewUseCases, Depends(_interview_usecase)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> AudioUploadResponse:
    """
    Загрузить аудио-ответ кандидата на вопрос.

    Сохраняет файл в <code>static/audio/interview_{id}/</code>.
    Поддерживает WebM (браузерная запись) и любой аудиоформат.
    Возвращает путь к файлу для передачи в <code>POST /interview/{id}/answers</code>.
    """
    try:
        await interview_usecase.get_interview(interview_id, current_user.id)
    except InterviewNotFound:
        raise HTTPException(status_code=404, detail="Interview not found")
    except AUTH_EXEPTIONS:
        raise

    audio_path = await handle_file_upload(file, f"audio/interview_{interview_id}")
    if not audio_path:
        raise HTTPException(status_code=400, detail="File upload failed")
    return AudioUploadResponse(audio_path=audio_path)


@interview_router.post("/{interview_id}/answers/{answer_id}/transcribe", response_model=GetAnswerSchema)
async def transcribe_answer(
    interview_id: int,
    answer_id: int,
    interview_usecase: Annotated[InterviewUseCases, Depends(_interview_usecase)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Answer:
    """
    Транскрибировать аудио уже сохранённого ответа.

    Читает файл из <code>audio_path</code> ответа, отправляет в Whisper,
    сохраняет результат в поле <code>transcript</code>.
    Требует AI-провайдер с поддержкой транскрипции (OpenAI).
    """
    if interview_usecase.ai is None:
        raise HTTPException(status_code=503, detail="AI provider is not configured")
    try:
        return await interview_usecase.transcribe_answer(interview_id, answer_id, current_user.id)
    except InterviewNotFound:
        raise HTTPException(status_code=404, detail="Interview not found")
    except AnswerNotFound:
        raise HTTPException(status_code=404, detail="Answer not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except AUTH_EXEPTIONS:
        raise
    except Exception as err:
        logging.exception(f"Transcription failed for answer {answer_id}: {err}")
        raise HTTPException(status_code=502, detail="Transcription failed")


@interview_router.post("/{interview_id}/answers/{answer_id}/analyze", response_model=GetAnalysisSchema, status_code=201)
async def analyze_answer(
    interview_id: int,
    answer_id: int,
    interview_usecase: Annotated[InterviewUseCases, Depends(_interview_usecase)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Analysis:
    """
    Запустить AI-анализ одного ответа.

    AI оценивает ответ кандидата по критериям вопроса и возвращает:
    оценку (0–10), резюме, сильные и слабые стороны, рекомендацию
    (<code>hire</code> / <code>consider</code> / <code>reject</code>).

    Анализ можно запустить в любой момент — как во время интервью,
    так и после завершения. Повторный запуск для одного ответа вернёт 409.
    """
    if interview_usecase.ai is None:
        raise HTTPException(status_code=503, detail="AI provider is not configured")
    try:
        return await interview_usecase.analyze_answer(interview_id, answer_id, current_user.id)
    except InterviewNotFound:
        raise HTTPException(status_code=404, detail="Interview not found")
    except AnswerNotFound:
        raise HTTPException(status_code=404, detail="Answer not found")
    except AnalysisAlreadyExists:
        raise HTTPException(status_code=409, detail="This answer has already been analyzed")
    except AUTH_EXEPTIONS:
        raise
    except Exception as err:
        logging.exception(f"Error analyzing answer {answer_id}. Error: {err}")
        raise HTTPException(status_code=502, detail="AI request failed")


@interview_router.post("/{interview_id}/analyze", response_model=list[GetAnalysisSchema], status_code=201)
async def analyze_all(
    interview_id: int,
    interview_usecase: Annotated[InterviewUseCases, Depends(_interview_usecase)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[Analysis]:
    """
    Запустить AI-анализ всех ответов интервью.

    Анализирует все ответы, у которых ещё нет анализа. Уже проанализированные
    ответы пропускаются и возвращаются как есть. Удобно вызывать после
    завершения интервью одним запросом.
    """
    if interview_usecase.ai is None:
        raise HTTPException(status_code=503, detail="AI provider is not configured")
    try:
        return await interview_usecase.analyze_all(interview_id, current_user.id)
    except InterviewNotFound:
        raise HTTPException(status_code=404, detail="Interview not found")
    except AUTH_EXEPTIONS:
        raise
    except Exception as err:
        logging.exception(f"Error analyzing all answers for interview {interview_id}. Error: {err}")
        raise HTTPException(status_code=502, detail="AI request failed")
