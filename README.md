# Interwiews

Open-source платформа для проведения интервью с AI-ассистентом. Разворачивается локально — данные компании никуда не уходят.

## Идея

HR-скрининг и технические интервью — это больная точка. Интервьюеры задают шаблонные вопросы, не всегда понимают что спрашивают, и субъективно оценивают ответы. Interwiews решает это:

- **Создаёшь план интервью** — набор вопросов под конкретную роль или задачу
- **Кандидат отвечает голосом** — запись транскрибируется через Whisper
- **AI анализирует ответ** — оценка по заданным критериям, сильные/слабые стороны, рекомендация
- **Подключаешь свой AI** — OpenAI, Anthropic или локальная модель через Ollama

Подходит не только для найма — любые структурированные опросы, оценка знаний, исследования.

## Возможности

- Планы интервью с кастомными вопросами (behavioral / technical / custom)
- Запись и транскрипция ответов (Whisper)
- AI-анализ каждого ответа с оценкой и критериями
- Настраиваемые критерии оценки
- Любой AI-провайдер через одну переменную окружения
- Полностью self-hosted — данные остаются у вас

## Быстрый старт

```bash
git clone <repo>
cd interwiews
cp .env.example .env  # заполни переменные
docker-compose up
```

Открой `http://localhost` в браузере.

## AI провайдеры

Переключение через переменные окружения:

```env
# OpenAI (Whisper + GPT)
AI_PROVIDER=openai
AI_API_KEY=sk-...

# Anthropic (Claude)
AI_PROVIDER=anthropic
AI_API_KEY=sk-ant-...

# Локально через Ollama (данные не покидают сервер)
AI_PROVIDER=ollama
AI_BASE_URL=http://localhost:11434
AI_MODEL=llama3
```

Транскрипция (Whisper) поддерживается через `AI_PROVIDER=openai`. При использовании Anthropic или Ollama транскрипция требует отдельного сервиса.

## Стек

- **Backend** — FastAPI, SQLAlchemy, Alembic, asyncpg
- **Frontend** — React, Vite, TypeScript, shadcn/ui
- **Инфраструктура** — Docker, PostgreSQL

## Структура проекта

```bash
interwiews/
├── backend/
│   ├── interwiews/
│   │   ├── providers/      # AI провайдеры (openai / anthropic / ollama)
│   │   ├── domain/         # бизнес-логика
│   │   ├── routers/        # API endpoints
│   │   └── infrastructure/ # БД, репозитории
│   └── migrations/
├── frontend/
└── docker-compose.yml
```

## Лицензия

MIT — форкай, деплой, адаптируй под свои нужды.
