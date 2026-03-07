import logging
import os
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from interwiews.common.logger import ch
from interwiews.infrastructure.database.connection import migrate
from interwiews.routers import api

logger = logging.getLogger("root")
logger.setLevel(logging.INFO)
logger.addHandler(ch)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await migrate()
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

api = APIRouter(
    prefix="/api",
    responses={404: {"description": "Page not found"}},
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
