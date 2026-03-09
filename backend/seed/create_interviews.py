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
    {
        "id": 3,
        "plan_id": 3,
        "candidate_name": "Дмитрий Кузнецов",
        "type": "technical",
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
    # --- Интервью 3: Дмитрий Кузнецов, Python стажёр, план 3 (вопросы id=6..15) ---
    {
        "id": 4,
        "interview_id": 3,
        "plan_id": 3,
        "question_id": 6,  # list vs tuple
        "answer": "Список — изменяемый, кортеж — нет. Список можно менять после создания, кортеж нельзя. Кортежи используют там, где данные не должны меняться, например для координат или возврата нескольких значений из функции. Ещё кортежи чуть быстрее по памяти.",
        "transcript": "Список — изменяемый, кортеж — нет. Список можно менять после создания, кортеж нельзя. Кортежи используют там, где данные не должны меняться, например для координат или возврата нескольких значений из функции. Ещё кортежи чуть быстрее по памяти.",
        "audio_path": None,
    },
    {
        "id": 5,
        "interview_id": 3,
        "plan_id": 3,
        "question_id": 7,  # virtual env
        "answer": "Виртуальное окружение изолирует зависимости проекта от системного Python. Создаю через python -m venv venv, активирую source venv/bin/activate, потом ставлю пакеты через pip. Это помогает когда разные проекты требуют разные версии одной библиотеки.",
        "transcript": "Виртуальное окружение изолирует зависимости проекта от системного Python. Создаю через python -m venv venv, активирую source venv/bin/activate, потом ставлю пакеты через pip. Это помогает когда разные проекты требуют разные версии одной библиотеки.",
        "audio_path": None,
    },
    {
        "id": 6,
        "interview_id": 3,
        "plan_id": 3,
        "question_id": 8,  # GET vs POST
        "answer": "GET передаёт параметры в URL, используется для получения данных. POST — в теле запроса, для отправки данных на сервер. GET кешируется браузером, POST — нет. Ещё GET ограничен по длине URL, а POST может передавать большие объёмы, например файлы.",
        "transcript": "GET передаёт параметры в URL, используется для получения данных. POST — в теле запроса, для отправки данных на сервер. GET кешируется браузером, POST — нет. Ещё GET ограничен по длине URL, а POST может передавать большие объёмы, например файлы.",
        "audio_path": None,
    },
    {
        "id": 7,
        "interview_id": 3,
        "plan_id": 3,
        "question_id": 9,  # Django vs Flask
        "answer": "Django — большой фреймворк, в нём уже есть ORM, админка, авторизация, всё готово из коробки. Flask — минималистичный микрофреймворк, нужно самому подключать всё что нужно. Для небольших сервисов или API я бы взял Flask, для полноценного сайта с авторизацией — Django.",
        "transcript": "Django — большой фреймворк, в нём уже есть ORM, админка, авторизация, всё готово из коробки. Flask — минималистичный микрофреймворк, нужно самому подключать всё что нужно. Для небольших сервисов или API я бы взял Flask, для полноценного сайта с авторизацией — Django.",
        "audio_path": None,
    },
    {
        "id": 8,
        "interview_id": 3,
        "plan_id": 3,
        "question_id": 10,  # Git
        "answer": "Git использую каждый день. Знаю commit, push, pull, branch, merge. Создаю ветку под каждую фичу, потом делаю merge в main. Конфликты приходилось решать вручную — смотришь что изменилось в обоих версиях и выбираешь нужное. Про rebase слышал, но на практике пока не использовал.",
        "transcript": "Git использую каждый день. Знаю commit, push, pull, branch, merge. Создаю ветку под каждую фичу, потом делаю merge в main. Конфликты приходилось решать вручную — смотришь что изменилось в обоих версиях и выбираешь нужное. Про rebase слышал, но на практике пока не использовал.",
        "audio_path": None,
    },
    {
        "id": 9,
        "interview_id": 3,
        "plan_id": 3,
        "question_id": 11,  # dict / word count
        "answer": "Можно разбить строку по пробелам через split(), потом пройтись циклом. Если слово уже есть в словаре — увеличиваю счётчик, если нет — добавляю с единицей. Или можно использовать collections.Counter — он это делает в одну строку.",
        "transcript": "Можно разбить строку по пробелам через split(), потом пройтись циклом. Если слово уже есть в словаре — увеличиваю счётчик, если нет — добавляю с единицей. Или можно использовать collections.Counter — он это делает в одну строку.",
        "audio_path": None,
    },
    {
        "id": 10,
        "interview_id": 3,
        "plan_id": 3,
        "question_id": 12,  # hardest project
        "answer": "Писал парсер для сайта с динамическим контентом — сначала пробовал requests и BeautifulSoup, но данные грузились через JavaScript. Пришлось разбираться с Selenium. Сложнее всего было настроить ожидание загрузки элементов — много времени ушло на это. Зато в итоге всё заработало и я узнал про implicit и explicit waits.",
        "transcript": "Писал парсер для сайта с динамическим контентом — сначала пробовал requests и BeautifulSoup, но данные грузились через JavaScript. Пришлось разбираться с Selenium. Сложнее всего было настроить ожидание загрузки элементов — много времени ушло на это. Зато в итоге всё заработало и я узнал про implicit и explicit waits.",
        "audio_path": None,
    },
    {
        "id": 11,
        "interview_id": 3,
        "plan_id": 3,
        "question_id": 13,  # code review
        "answer": "Если мне указывают на ошибку — стараюсь понять почему это ошибка, а не просто исправить механически. Иногда не сразу соглашаюсь, но если объяснят — принимаю. Думаю что ревью это хорошо, помогает учиться. Пока опыта в командной разработке немного, но в учебных проектах такое было.",
        "transcript": "Если мне указывают на ошибку — стараюсь понять почему это ошибка, а не просто исправить механически. Иногда не сразу соглашаюсь, но если объяснят — принимаю. Думаю что ревью это хорошо, помогает учиться. Пока опыта в командной разработке немного, но в учебных проектах такое было.",
        "audio_path": None,
    },
    {
        "id": 12,
        "interview_id": 3,
        "plan_id": 3,
        "question_id": 14,  # self-learning
        "answer": "В основном смотрю документацию и YouTube, иногда Habr. Сейчас прохожу курс по FastAPI на Udemy. Если застреваю на проблеме — сначала пробую сам разобраться минут 20-30, потом Stack Overflow или ChatGPT. Стараюсь не просто копировать решение, а понять как оно работает.",
        "transcript": "В основном смотрю документацию и YouTube, иногда Habr. Сейчас прохожу курс по FastAPI на Udemy. Если застреваю на проблеме — сначала пробую сам разобраться минут 20-30, потом Stack Overflow или ChatGPT. Стараюсь не просто копировать решение, а понять как оно работает.",
        "audio_path": None,
    },
    {
        "id": 13,
        "interview_id": 3,
        "plan_id": 3,
        "question_id": 15,  # motivation
        "answer": "Мне нравится веб-разработка и Python, хочу попасть именно в эту область. Видел ваши проекты — интересный стек, Django и FastAPI. Хочу получить реальный опыт в команде, понять как устроена разработка в компании, не в учебных проектах. Готов работать усердно и учиться.",
        "transcript": "Мне нравится веб-разработка и Python, хочу попасть именно в эту область. Видел ваши проекты — интересный стек, Django и FastAPI. Хочу получить реальный опыт в команде, понять как устроена разработка в компании, не в учебных проектах. Готов работать усердно и учиться.",
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
    # --- Анализ ответов Дмитрия Кузнецова (interview 3) ---
    {
        "id": 4,
        "answer_id": 4,
        "score": 6.5,
        "summary": "Базовое понимание разницы list/tuple. Упомянул изменяемость и типичные кейсы, но поверхностно.",
        "strengths": '["Правильное определение изменяемости", "Привёл пример использования кортежа", "Упомянул производительность"]',
        "weaknesses": '["Не упомянул хешируемость кортежей и возможность использования как ключа словаря", "Не сказал про распаковку", "Ответ краткий без деталей"]',
        "recomendation": "consider",
    },
    {
        "id": 5,
        "answer_id": 5,
        "score": 7.5,
        "summary": "Хорошее понимание виртуальных окружений: зачем нужны и как создавать. Команды знает правильно.",
        "strengths": '["Правильно объяснил цель изоляции зависимостей", "Верные команды: venv, activate, pip", "Привёл практический пример конфликта версий"]',
        "weaknesses": '["Не упомянул requirements.txt и pip freeze", "Не знает про uv или poetry как современные альтернативы"]',
        "recomendation": "hire",
    },
    {
        "id": 6,
        "answer_id": 6,
        "score": 7.0,
        "summary": "Уверенный ответ про GET/POST. Основные отличия назвал верно, понимает кеширование и ограничения.",
        "strengths": '["Верно описал передачу параметров", "Упомянул кеширование", "Сказал про ограничение длины URL и файлы"]',
        "weaknesses": '["Не упомянул идемпотентность", "Не затронул другие методы: PUT, DELETE, PATCH", "Не сказал про безопасность — пароль в URL"]',
        "recomendation": "hire",
    },
    {
        "id": 7,
        "answer_id": 7,
        "score": 6.0,
        "summary": "Понимает разницу Django/Flask на поверхностном уровне. Знает ключевые особенности, но без опыта работы с обоими.",
        "strengths": '["Правильно охарактеризовал Django как batteries-included", "Верно назвал Flask микрофреймворком", "Может выбрать подходящий инструмент под задачу"]',
        "weaknesses": '["Нет реального опыта с Django", "Не упомянул шаблонизаторы, миграции, middleware", "Ответ теоретический без практических примеров"]',
        "recomendation": "consider",
    },
    {
        "id": 8,
        "answer_id": 8,
        "score": 6.5,
        "summary": "Базовые навыки Git есть. Основной workflow знает, конфликты решал. Rebase и более продвинутые команды не освоены.",
        "strengths": '["Знает базовые команды", "Практикует feature-branch workflow", "Решал конфликты слияния"]',
        "weaknesses": '["Не знает rebase на практике", "Не упомянул git log, stash, cherry-pick", "Нет опыта с pull request процессом в команде"]',
        "recomendation": "consider",
    },
    {
        "id": 9,
        "answer_id": 9,
        "score": 8.0,
        "summary": "Отличный ответ на алгоритмическую задачу. Предложил два варианта решения, знает стандартную библиотеку.",
        "strengths": '["Правильный базовый алгоритм со split и циклом", "Знает collections.Counter", "Лаконичное решение"]',
        "weaknesses": '["Не упомянул обработку пунктуации и разных регистров", "Не оценил сложность O(n)"]',
        "recomendation": "hire",
    },
    {
        "id": 10,
        "answer_id": 10,
        "score": 7.5,
        "summary": "Хороший рассказ о реальном сложном проекте. Видна способность разбираться в незнакомых инструментах самостоятельно.",
        "strengths": '["Конкретный проект с реальной проблемой", "Самостоятельно разобрался с новым инструментом", "Сделал выводы и усвоил новые знания"]',
        "weaknesses": '["Проект учебный, не продакшн", "Не упомянул как документировал или тестировал решение"]',
        "recomendation": "hire",
    },
    {
        "id": 11,
        "answer_id": 11,
        "score": 7.0,
        "summary": "Зрелое отношение к обратной связи для стажёра. Готов принимать критику и учиться, не просто соглашается механически.",
        "strengths": '["Стремится понять причину замечания", "Отстаивает позицию аргументированно", "Позитивное отношение к ревью как к инструменту роста"]',
        "weaknesses": '["Мало реального командного опыта", "Пока не прошёл настоящий production code review"]',
        "recomendation": "hire",
    },
    {
        "id": 12,
        "answer_id": 12,
        "score": 7.0,
        "summary": "Хороший подход к самообучению. Использует официальную документацию, проходит структурированный курс, умеет отлаживать проблемы.",
        "strengths": '["Сначала пробует сам, потом ищет помощь", "Использует разные источники", "Стремится понять, не просто скопировать"]',
        "weaknesses": '["Не упомянул чтение чужого кода и open source", "Нет привычки вести заметки или конспекты"]',
        "recomendation": "hire",
    },
    {
        "id": 13,
        "answer_id": 13,
        "score": 7.5,
        "summary": "Мотивация искренняя и конкретная. Кандидат изучил стек компании, готов к росту. Хороший потенциал для стажёра.",
        "strengths": '["Конкретный интерес к технологиям компании", "Честная цель — получить реальный опыт", "Правильная установка на упорную работу"]',
        "weaknesses": '["Не рассказал о конкретных своих проектах как доказательстве интереса", "Мог бы упомянуть что именно смотрел из работ компании"]',
        "recomendation": "hire",
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
