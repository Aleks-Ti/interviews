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
        "status": "published",
    },
    {
        "id": 2,
        "name": "HR Screening (General)",
        "description": "Базовый скрининг для любой роли. Мотивация, ожидания, культурный фит.",
        "status": "published",
    },
    {
        "id": 3,
        "name": "Python Стажёр — Веб-студия",
        "description": "Интервью для стажёра Python в веб-студию. Проверяем базовые знания языка, понимание веба, Git, умение учиться и вписаться в команду. Не ждём глубокой экспертизы — смотрим на потенциал и мышление.",
        "status": "published",
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
    # Plan 3 — Python Стажёр Веб-студия
    {
        "id": 6,
        "plan_id": 3,
        "text": "Чем list отличается от tuple в Python? Когда ты используешь одно, а когда другое?",
        "type": "technical",
        "criteria": ["mutability understanding", "correct use cases", "knows at least one practical example"],
    },
    {
        "id": 7,
        "plan_id": 3,
        "text": "Что такое виртуальное окружение в Python и зачем оно нужно?",
        "type": "technical",
        "criteria": ["understands isolation concept", "knows how to create (venv/pip)", "explains why dependencies matter"],
    },
    {
        "id": 8,
        "plan_id": 3,
        "text": "Объясни разницу между GET и POST запросами. Когда ты используешь каждый из них?",
        "type": "technical",
        "criteria": ["correct semantics", "knows about request body vs query params", "real-world example"],
    },
    {
        "id": 9,
        "plan_id": 3,
        "text": "Ты работал с Django или Flask? Расскажи что знаешь — хотя бы в теории.",
        "type": "technical",
        "criteria": ["awareness of at least one framework", "understands MVC/MTV concept", "honest about experience level"],
    },
    {
        "id": 10,
        "plan_id": 3,
        "text": "Какие команды Git ты используешь чаще всего? Что такое ветка и зачем она нужна?",
        "type": "technical",
        "criteria": ["knows basic commands (commit, push, pull, branch)", "understands branching concept", "real workflow experience"],
    },
    {
        "id": 11,
        "plan_id": 3,
        "text": "Что такое словарь (dict) в Python? Как бы ты посчитал количество вхождений каждого слова в тексте?",
        "type": "technical",
        "criteria": ["understands key-value structure", "can write or describe working solution", "knows about dict methods"],
    },
    {
        "id": 12,
        "plan_id": 3,
        "text": "Расскажи про свой самый сложный учебный проект. Что было трудно и как справился?",
        "type": "behavioral",
        "criteria": ["concreteness (not abstract)", "problem-solving mindset", "takes ownership of difficulties"],
    },
    {
        "id": 13,
        "plan_id": 3,
        "text": "Как ты реагируешь когда тебе говорят что твой код написан плохо и нужно переписать?",
        "type": "behavioral",
        "criteria": ["no defensiveness", "open to feedback", "asks clarifying questions rather than argues"],
    },
    {
        "id": 14,
        "plan_id": 3,
        "text": "Как ты учишься самостоятельно? Что изучал в последние пару месяцев?",
        "type": "behavioral",
        "criteria": ["self-directed learning", "can name specific resource or topic", "curiosity and initiative"],
    },
    {
        "id": 15,
        "plan_id": 3,
        "text": "Почему хочешь в веб-разработку и почему именно к нам в студию?",
        "type": "custom",
        "criteria": ["genuine motivation (not just 'money')", "knows something about the company", "realistic expectations"],
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
                    INSERT INTO public.plans (id, name, description, date_create, date_update, created_by_user_id, status)
                    VALUES (:id, :name, :description, :date_create, :date_update, :created_by_user_id, :status)
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

        await session.execute(text("SELECT setval(pg_get_serial_sequence('plans', 'id'), MAX(id)) FROM plans"))
        await session.execute(text("SELECT setval(pg_get_serial_sequence('questions', 'id'), MAX(id)) FROM questions"))
        await session.commit()

    print("plans loaded!\n")
