import logging
import time
import uuid
from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from src.core.logger import request_id_context

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        log_request_body: bool = False,
        log_slow_requests: bool = True,
        slow_request_threshold: float = 1.0,
    ) -> None:
        super().__init__(app)
        self.log_request_body = log_request_body
        self.log_slow_requests = log_slow_requests
        self.slow_request_threshold = slow_request_threshold

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request_id_context.set(request_id)

        start_time = time.time()
        request_body = None

        if self.log_request_body:
            try:
                body_bytes = await request.body()
                request_body = body_bytes.decode("utf-8", errors="replace")[:1000]
                request._body = body_bytes
            except (UnicodeDecodeError, ValueError):
                pass

        logger.info(
            "Incoming request",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "query_params": str(request.query_params) if request.query_params else None,
                "client_host": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
                **({"body": request_body} if request_body else {}),
            },
        )

        try:
            response = await call_next(request)
            process_time = time.time() - start_time

            log_data = {
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "process_time": round(process_time, 3),
            }

            if self.log_slow_requests and process_time > self.slow_request_threshold:
                logger.warning(
                    "Slow request detected",
                    extra={**log_data, "threshold": self.slow_request_threshold},
                )
            else:
                logger.info("Request completed", extra=log_data)

            response.headers["X-Request-ID"] = request_id
            return response

        except Exception as exc:
            process_time = time.time() - start_time
            logger.error(
                "Request failed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "process_time": round(process_time, 3),
                    "error": str(exc),
                    "error_type": type(exc).__name__,
                },
                exc_info=True,
            )
            raise
