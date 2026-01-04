from collections.abc import Callable
from typing import Any

from fastapi_cache.decorator import cache

from src.core.settings import settings


def cached(
    expire: int = settings.CACHE_DEFAULT_TTL,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Helper decorator for fastapi-cache2 with default TTL from settings.

    Usage:
        @router.get("/")
        @cached()
        async def endpoint():
            return {"data": "value"}

    Args:
        expire: Cache TTL in seconds (defaults to CACHE_DEFAULT_TTL)

    Returns:
        fastapi-cache2 cache decorator
    """
    if not settings.CACHE_ENABLED:

        def noop_decorator(func):
            return func

        return noop_decorator

    return cache(expire=expire)
