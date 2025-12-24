import logging
from collections.abc import Callable

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

from src.core.settings import settings

logger = logging.getLogger(__name__)

if settings.RATE_LIMIT_STORAGE_URI:
    limiter = Limiter(
        key_func=get_remote_address,
        storage_uri=settings.RATE_LIMIT_STORAGE_URI,
        headers_enabled=settings.RATE_LIMIT_HEADERS_ENABLED,
    )
    logger.info(
        "Rate limiter initialized with Redis storage: %s",
        settings.RATE_LIMIT_STORAGE_URI,
    )
else:
    limiter = Limiter(
        key_func=get_remote_address,
        headers_enabled=settings.RATE_LIMIT_HEADERS_ENABLED,
    )
    logger.warning(
        "Rate limiter using in-memory storage. "
        "This is not recommended for production with multiple workers. "
        "Set RATE_LIMIT_STORAGE_URI to use Redis."
    )


def get_rate_limit_exceeded_handler() -> Callable:
    return _rate_limit_exceeded_handler


def rate_limit(limit: str | None = None) -> Callable:
    """Decorator for applying rate limits to endpoints.

    Args:
        limit: Rate limit string (e.g., '10/minute', '100/hour').
            If None, uses the default from settings.

    Returns:
        Decorator function that can be applied to FastAPI route handlers.

    Example:
        @router.get("/api/v1/endpoint")
        @rate_limit("10/minute")
        async def endpoint(request: Request, response: Response):
            return {"data": "value"}
    """
    if not settings.RATE_LIMIT_ENABLED:

        def noop_decorator(func):
            return func

        return noop_decorator

    limit_str = limit or settings.RATE_LIMIT_DEFAULT
    return limiter.limit(limit_str)
