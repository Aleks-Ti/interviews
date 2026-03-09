import json
import os
import sys
from datetime import datetime

from sqlalchemy import text

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from interviews.infrastructure.database.connection import async_session_maker

# Данные интервью — привязаны к плану 1 (Python Backend)
# conducted_by подтягивается из БД по email администратора

INTERVIEWS = [
    {
        "id": 1,
        "plan_id": 1,
        "candidate_name": "Иван Петров",
        "type": "technical",
        "status": "completed",
    },
    {
        "id": 2,
        "plan_id": 2,
        "candidate_name": "Мария Соколова",
        "type": "behavioral",
        "status": "completed",
    },
]

# answer = текст ответа, transcript = то что вернул бы Whisper (одно и то же для сида)
ANSWERS = [
    {
        "id": 1,
        "interview_id": 1,
        "plan_id": 1,
        "question_id": 1,
        "answer": "asyncio использует однопоточную модель с event loop, threading — настоящие потоки ОС. asyncio лучше для I/O-bound задач вроде HTTP-запросов и работы с БД, threading — когда нужен параллелизм с блокирующим кодом.",
        "transcript": "asyncio использует однопоточную модель с event loop, threading — настоящие потоки ОС. asyncio лучше для I/O-bound задач вроде HTTP-запросов и работы с БД, threading — когда нужен параллелизм с блокирующим кодом.",
        "audio_path": None,
    },
    {
        "id": 2,
        "interview_id": 1,
        "plan_id": 1,
        "question_id": 2,
        "answer": "Lazy loading подгружает связанные объекты по запросу, eager loading — сразу через JOIN. В asyncio-среде lazy loading вызывает проблемы с DetachedInstanceError, поэтому я обычно использую selectinload или joinedload через options().",
        "transcript": "Lazy loading подгружает связанные объекты по запросу, eager loading — сразу через JOIN. В asyncio-среде lazy loading вызывает проблемы с DetachedInstanceError, поэтому я обычно использую selectinload или joinedload через options().",
        "audio_path": None,
    },
    {
        "id": 3,
        "interview_id": 2,
        "plan_id": 2,
        "question_id": 4,
        "answer": "Текущий проект завершён, хочу расти в сторону архитектуры и работы с высоконагруженными системами. На нынешнем месте такой возможности нет.",
        "transcript": "Текущий проект завершён, хочу расти в сторону архитектуры и работы с высоконагруженными системами. На нынешнем месте такой возможности нет.",
        "audio_path": None,
    },
]

ANALYSES = [
    {
        "id": 1,
        "answer_id": 1,
        "score": 8.5,
        "summary": "Кандидат хорошо понимает разницу между моделями конкурентности, привёл конкретные примеры применения.",
        "strengths": '["Чёткое разграничение asyncio и threading", "Понимание I/O-bound vs CPU-bound", "Практический контекст"]',
        "weaknesses": '["Не упомянул GIL", "Не затронул multiprocessing как альтернативу"]',
        "recomendation": "hire",
    },
    {
        "id": 2,
        "answer_id": 2,
        "score": 9.0,
        "summary": "Отличный ответ — кандидат знает не только теорию, но и практические проблемы в asyncio-контексте.",
        "strengths": '["Знание DetachedInstanceError", "Конкретные методы: selectinload, joinedload", "Понимание производительности"]',
        "weaknesses": '["Не упомянул subqueryload"]',
        "recomendation": "hire",
    },
    {
        "id": 3,
        "answer_id": 3,
        "score": 7.0,
        "summary": "Мотивация понятна и профессиональна, ответ честный без негатива про текущего работодателя.",
        "strengths": '["Чёткая карьерная цель", "Без негатива", "Конкретная причина"]',
        "weaknesses": '["Не рассказал что именно привлекает в нашей компании"]',
        "recomendation": "consider",
    },
]


async def interviews() -> None:
    print("\nRun script[interviews loaded].")
    now = datetime.now()

    async with async_session_maker() as session:
        # Берём id любого существующего пользователя как conducted_by
        result = await session.execute(text("SELECT id FROM public.users LIMIT 1"))
        row = result.fetchone()
        if row is None:
            raise RuntimeError("Нет пользователей в БД. Сначала запусти create_admin.")
        conducted_by = row[0]

        for interview in INTERVIEWS:
            await session.execute(
                text("""
                    INSERT INTO public.interviews
                        (id, plan_id, candidate_name, type, status, conducted_by, date_create, date_update)
                    VALUES
                        (:id, :plan_id, :candidate_name, :type, :status, :conducted_by, :date_create, :date_update)
                    ON CONFLICT (id) DO NOTHING
                """),
                {
                    **interview,
                    "conducted_by": conducted_by,
                    "date_create": now,
                    "date_update": now,
                },
            )

        for answer in ANSWERS:
            await session.execute(
                text("""
                    INSERT INTO public.answers
                        (id, interview_id, question_id, answer, transcript, audio_path, date_create, date_update)
                    VALUES
                        (:id, :interview_id, :question_id, :answer, :transcript, :audio_path, :date_create, :date_update)
                    ON CONFLICT (id) DO NOTHING
                """),
                {**answer, "date_create": now, "date_update": now},
            )

        for analysis in ANALYSES:
            await session.execute(
                text("""
                    INSERT INTO public.analysis
                        (id, answer_id, score, summary, strengths, weaknesses, recomendation)
                    VALUES
                        (:id, :answer_id, :score, :summary, CAST(:strengths AS jsonb), CAST(:weaknesses AS jsonb), :recomendation)
                    ON CONFLICT (id) DO NOTHING
                """),
                analysis,
            )

        await session.execute(text("SELECT setval(pg_get_serial_sequence('interviews', 'id'), MAX(id)) FROM interviews"))
        await session.execute(text("SELECT setval(pg_get_serial_sequence('answers', 'id'), MAX(id)) FROM answers"))
        await session.execute(text("SELECT setval(pg_get_serial_sequence('analysis', 'id'), MAX(id)) FROM analysis"))
        await session.commit()

    print("interviews loaded!\n")
