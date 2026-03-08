import json
import os
import sys
from datetime import datetime

from sqlalchemy import text

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from interviews.infrastructure.database.connection import async_session_maker


PLANS = [
    {
        "id": 1,
        "name": "Python Backend Developer",
        "description": "Техническое интервью для бэкенд-разработчиков на Python. Охватывает asyncio, ORM, архитектуру и опыт решения реальных задач.",
    },
    {
        "id": 2,
        "name": "HR Screening (General)",
        "description": "Базовый скрининг для любой роли. Мотивация, ожидания, культурный фит.",
    },
]

QUESTIONS = [
    # Plan 1 — Python Backend
    {
        "id": 1,
        "plan_id": 1,
        "text": "Объясни разницу между asyncio и threading в Python. Когда ты выберешь одно вместо другого?",
        "type": "technical",
        "criteria": ["correctness", "depth of knowledge", "practical examples"],
    },
    {
        "id": 2,
        "plan_id": 1,
        "text": "Как SQLAlchemy обрабатывает lazy и eager loading? В чём разница и когда использовать каждый подход?",
        "type": "technical",
        "criteria": ["correctness", "ORM understanding", "performance awareness"],
    },
    {
        "id": 3,
        "plan_id": 1,
        "text": "Расскажи о случае, когда тебе пришлось оптимизировать медленные запросы к базе данных.",
        "type": "behavioral",
        "criteria": ["problem-solving approach", "technical depth", "measurable outcome"],
    },
    # Plan 2 — HR Screening
    {
        "id": 4,
        "plan_id": 2,
        "text": "Почему ты сейчас рассматриваешь новые предложения? Что тебя мотивирует в смене работы?",
        "type": "behavioral",
        "criteria": ["honesty", "motivation clarity", "cultural fit signals"],
    },
    {
        "id": 5,
        "plan_id": 2,
        "text": "Какие у тебя зарплатные ожидания и когда ты готов выйти?",
        "type": "custom",
        "criteria": ["clarity", "realism", "flexibility"],
    },
]


async def plans() -> None:
    print("\nRun script[plans loaded].")
    now = datetime.now()

    async with async_session_maker() as session:
        user_id = await session.execute(text("SELECT id FROM public.users WHERE email = 'admin@admin.admin'"))
        user_id = user_id.scalar()
        for plan in PLANS:
            await session.execute(
                text("""
                    INSERT INTO public.plans (id, name, description, date_create, date_update, created_by_user_id)
                    VALUES (:id, :name, :description, :date_create, :date_update, :created_by_user_id)
                    ON CONFLICT (id) DO NOTHING
                """),
                {**plan, "date_create": now, "date_update": now, "created_by_user_id": user_id},
            )

        for question in QUESTIONS:
            await session.execute(
                text("""
                    INSERT INTO public.questions (id, plan_id, text, type, criteria, date_create, date_update)
                    VALUES (:id, :plan_id, :text, :type, CAST(:criteria AS jsonb), :date_create, :date_update)
                    ON CONFLICT (id) DO NOTHING
                """),
                {**question, "criteria": json.dumps(question["criteria"]), "date_create": now, "date_update": now},
            )

        await session.commit()

    print("plans loaded!\n")
