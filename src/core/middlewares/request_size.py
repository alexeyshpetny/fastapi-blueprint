import logging
from collections.abc import Awaitable, Callable

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, max_size: int) -> None:
        super().__init__(app)
        self.max_size = max_size

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        content_length = request.headers.get("content-length")
        if not content_length:
            return await call_next(request)

        try:
            size = int(content_length)
        except ValueError:
            return await call_next(request)

        if size <= self.max_size:
            return await call_next(request)

        logger.warning(
            "Request body size exceeds limit",
            extra={
                "request_id": request.headers.get("X-Request-ID", "unknown"),
                "path": request.url.path,
                "size": size,
                "max_size": self.max_size,
            },
        )

        return JSONResponse(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            content={
                "error": "Request entity too large",
                "message": (
                    f"Request body size ({size} bytes) exceeds maximum allowed size ({self.max_size} bytes). "
                    "Please reduce the size of the request body."
                ),
                "max_size": self.max_size,
            },
        )
