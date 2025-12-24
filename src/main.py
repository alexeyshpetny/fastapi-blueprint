import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from slowapi.errors import RateLimitExceeded

from src.api.router import router
from src.cache.redis import cache_client, close_cache
from src.core.exceptions import add_exception_handlers
from src.core.logger import setup_logging
from src.core.middlewares import (
    LoggingMiddleware,
    RequestSizeLimitMiddleware,
    SecurityHeadersMiddleware,
)
from src.core.settings import settings
from src.db.db import engine
from src.rate_limit import get_rate_limit_exceeded_handler, limiter

setup_logging()

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("Application startup", extra={"version": settings.DOC_VERSION})
    if settings.CACHE_ENABLED:
        FastAPICache.init(
            RedisBackend(cache_client),
            prefix=settings.CACHE_KEY_PREFIX,
        )
        logger.info("FastAPI Cache initialized with Redis backend")
    yield
    logger.info("Application shutdown")
    await close_cache()
    await engine.dispose()


def create_app() -> FastAPI:
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

    if settings.TRUSTED_HOSTS_ENABLED:
        if not settings.TRUSTED_HOSTS:
            logger.warning(
                "TRUSTED_HOSTS_ENABLED=True but TRUSTED_HOSTS is empty. "
                "TrustedHostMiddleware will reject all requests. "
                "Set TRUSTED_HOSTS to enable host validation."
            )
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.TRUSTED_HOSTS,
        )
        logger.info(f"TrustedHostMiddleware enabled with hosts: {settings.TRUSTED_HOSTS}")

    app.add_middleware(
        RequestSizeLimitMiddleware,
        max_size=settings.MAX_REQUEST_BODY_SIZE,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ALLOW_ORIGINS,
        allow_methods=settings.CORS_ALLOW_METHODS,
        allow_headers=settings.CORS_ALLOW_HEADERS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        max_age=settings.CORS_MAX_AGE,
    )

    if settings.SECURITY_HEADERS_ENABLED:
        app.add_middleware(
            SecurityHeadersMiddleware,
            x_content_type_options=settings.SECURITY_X_CONTENT_TYPE_OPTIONS,
            x_frame_options=settings.SECURITY_X_FRAME_OPTIONS,
            x_xss_protection=settings.SECURITY_X_XSS_PROTECTION,
            strict_transport_security=settings.SECURITY_STRICT_TRANSPORT_SECURITY,
            content_security_policy=settings.SECURITY_CONTENT_SECURITY_POLICY,
            referrer_policy=settings.SECURITY_REFERRER_POLICY,
            permissions_policy=settings.SECURITY_PERMISSIONS_POLICY,
        )

    if settings.RATE_LIMIT_ENABLED:
        app.state.limiter = limiter
        app.add_exception_handler(RateLimitExceeded, get_rate_limit_exceeded_handler())
        logger.info(f"Rate limiting enabled with default limit: {settings.RATE_LIMIT_DEFAULT}")

    add_exception_handlers(app)

    app.include_router(router)
    return app


application = create_app()
