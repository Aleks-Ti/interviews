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

## Разработка

### Требования

- Python 3.12+, [uv](https://github.com/astral-sh/uv)
- Node.js 20+, npm
- Docker (для БД)
- [Task](https://taskfile.dev) (`task`)

### 1. Переменные окружения

```bash
cp .env.example .env
# заполни AI_API_KEY и при необходимости остальные параметры
```

### 2. База данных

Запустить PostgreSQL в Docker (данные сохраняются между перезапусками):

```bash
cd backend
task postgres:up:volume
```

Применить миграции и загрузить начальные данные:

```bash
task alembic:migrate
task seed:load
```

Остановить БД:

```bash
task postgres:stop
```

### 3. Backend

Установить зависимости (один раз):

```bash
cd backend
task uv:install:all
```

Запустить в режиме разработки (с hot-reload):

```bash
cd backend
task start
```

Запустить в продакшн-режиме (uvicorn, 4 воркера):

```bash
cd backend
source .env
uv run gunicorn --bind $HOST:$PORT "$APP_MODULE" -k uvicorn.workers.UvicornWorker -w 4
```

API будет доступно по адресу `http://localhost:8000`.

### 4. Frontend

```bash
cd frontend
npm install
npm run dev
```

Фронт поднимается на `http://localhost:3000` по умолчанию. Для другого порта:

```bash
npm run dev -- -p 3001
```

---

## Лицензия

MIT — форкай, деплой, адаптируй под свои нужды.


Resume this session with:
claude --resume 03f5be9e-6615-4dbc-a789-62a9105fb22b
