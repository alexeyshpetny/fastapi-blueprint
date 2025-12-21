import logging
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from src.adapters.request_cache_adapter import RequestCacheAdapter

logger = logging.getLogger(__name__)


class CacheMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        request_cache_adapter: RequestCacheAdapter | None = None,
    ) -> None:
        super().__init__(app)
        self._request_cache_adapter = request_cache_adapter

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if self._request_cache_adapter is None:
            return await call_next(request)

        try:
            if not self._request_cache_adapter.should_cache(request):
                return await call_next(request)

            cache_key = self._request_cache_adapter.generate_cache_key(request)
            cached_response = await self._request_cache_adapter.get_cached_response(cache_key, request.url.path)
            if cached_response is not None:
                return cached_response

            response = await call_next(request)
            return await self._request_cache_adapter.cache_response(cache_key, response, request.url.path)
        except Exception as e:
            logger.error(f"Cache middleware error: {e}", exc_info=True, extra={"path": request.url.path})
            return await call_next(request)
