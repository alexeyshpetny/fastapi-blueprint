import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.router import router
from src.cache.redis import close_cache
from src.core.exceptions import add_exception_handlers
from src.core.logger import setup_logging
from src.core.middlewares import CacheMiddleware, LoggingMiddleware
from src.core.settings import settings
from src.db.db import engine
from src.dependencies.cache_dependency import get_request_cache_adapter

setup_logging()

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("Application startup", extra={"version": settings.DOC_VERSION})
    yield
    logger.info("Application shutdown")
    await close_cache()
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
    LoggingMiddleware,
    log_request_body=settings.LOG_REQUEST_BODY,
    log_slow_requests=settings.LOG_SLOW_REQUESTS,
    slow_request_threshold=settings.LOG_SLOW_REQUEST_THRESHOLD,
)
app.add_middleware(
    CacheMiddleware,
    request_adapter=get_request_cache_adapter(
        enabled=settings.CACHE_MIDDLEWARE_ENABLED,
        cache_enabled=settings.CACHE_ENABLED,
        ttl=settings.CACHE_MIDDLEWARE_TTL,
        exclude_paths=settings.CACHE_MIDDLEWARE_EXCLUDE_PATHS,
        key_prefix=settings.CACHE_MIDDLEWARE_KEY_PREFIX,
    ),
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOW_ORIGINS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    max_age=settings.CORS_MAX_AGE,
)

add_exception_handlers(app)

app.include_router(router)
