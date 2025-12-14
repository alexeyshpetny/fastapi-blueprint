from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.router import router
from src.core.settings import settings
from src.db.db import engine


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(
    title=settings.DOC_TITLE,
    version=settings.DOC_VERSION,
    description=settings.DOC_DESCRIPTION,
    openapi_url=settings.DOC_OPENAPI_URL,
    docs_url=settings.DOC_SWAGGER_URL,
    redoc_url=settings.DOC_REDOC_URL,
    debug=settings.DEBUG,
    lifespan=lifespan,
)
app.openapi_version = settings.DOC_OPENAPI_VERSION
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOW_ORIGINS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    max_age=settings.CORS_MAX_AGE,
)
app.include_router(router)
