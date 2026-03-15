import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from interviews.core.logger import ch
from interviews.infrastructure.database.connection import migrate
from interviews.routers import api

logger = logging.getLogger("root")
logger.setLevel(logging.INFO)
logger.addHandler(ch)


async def _run_seeds():
    from seed.create_roles import role
    from seed.create_admin import user
    from seed.create_plans import plans
    from seed.create_interviews import interviews
    await role()
    await user()
    await plans()
    await interviews()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await migrate()
    try:
        await _run_seeds()
    except Exception:
        logger.exception("Seed failed (non-fatal)")
    yield


if os.environ.get("ENV") == "prod":
    app = FastAPI(
        title="interwies API",
        openapi_url=None,
        docs_url=None,
        redoc_url=None,
        lifespan=lifespan,
    )
else:
    app = FastAPI(
        title="interwies API",
        openapi_url="/api/openapi.json",
        docs_url="/api/docs",
        lifespan=lifespan,
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=[
        "Content-Type",
        "Set-Cookie",
        "Access-Control-Allow-Headers",
        "Access-Control-Allow-Origin",
        "Authorization",
    ],
)

app.include_router(api)

static_dir = Path("static")
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
