import asyncio
import logging
from collections.abc import Callable
from functools import wraps
from typing import Any

logger = logging.getLogger(__name__)


def handle_exceptions(exceptions: tuple[type[Exception], ...], default: Any = None) -> Callable:
    """Decorator to handle specified exceptions and return a default value.

    Works with both synchronous and asynchronous functions.

    Args:
        exceptions: Tuple of exception types to handle
        default: Value to return when an exception is caught

    Example:
        @handle_exceptions((KeyError, ValueError), default=None)
        async def my_function():
            ...
    """

    def decorator(func: Callable) -> Callable:
        if asyncio.iscoroutinefunction(func):

            @wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any | None:
                try:
                    return await func(*args, **kwargs)
                except exceptions as err:
                    logger.exception(
                        "Exception caught in async function",
                        extra={"exception": err, "function": func.__name__},
                    )
                    return default

            return async_wrapper

        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any | None:
            try:
                return func(*args, **kwargs)
            except exceptions as err:
                logger.exception(
                    "Exception caught in sync function",
                    extra={"exception": err, "function": func.__name__},
                )
                return default

        return sync_wrapper

    return decorator
