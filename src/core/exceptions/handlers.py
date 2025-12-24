import logging
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError as PydanticValidationError
from starlette.responses import JSONResponse

from src.core.exceptions.exceptions import ApplicationError
from src.core.settings import settings

logger = logging.getLogger(__name__)


def _get_request_id(request: Request) -> str:
    return request.headers.get("X-Request-ID", "unknown")


def add_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def request_validation_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        """Handle FastAPI request validation errors."""
        request_id = _get_request_id(request)
        errors = exc.errors()

        logger.warning(
            "Request validation failed",
            extra={
                "request_id": request_id,
                "path": request.url.path,
                "method": request.method,
                "errors": errors,
            },
        )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "Validation failed",
                "details": {"validation_errors": errors},
                "request_id": request_id,
            },
        )

    @app.exception_handler(PydanticValidationError)
    async def pydantic_validation_handler(request: Request, exc: PydanticValidationError) -> JSONResponse:
        """Handle Pydantic validation errors."""
        request_id = _get_request_id(request)
        errors = exc.errors()

        logger.warning(
            "Pydantic validation failed",
            extra={
                "request_id": request_id,
                "path": request.url.path,
                "method": request.method,
                "errors": errors,
            },
        )

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "Invalid input",
                "details": {"validation_errors": errors},
                "request_id": request_id,
            },
        )

    @app.exception_handler(ApplicationError)
    async def application_error_handler(request: Request, exc: ApplicationError) -> JSONResponse:
        """Handle all custom application errors."""
        request_id = _get_request_id(request)
        log_level = logger.error if exc.status_code >= 500 else logger.warning

        log_level(
            "Application error occurred",
            extra={
                "request_id": request_id,
                "path": request.url.path,
                "method": request.method,
                "status_code": exc.status_code,
                "error": exc.message,
                "details": exc.details,
            },
            exc_info=False,
        )

        content: dict[str, Any] = {"error": exc.message, "request_id": request_id}
        if exc.details is not None:
            content["details"] = exc.details

        return JSONResponse(status_code=exc.status_code, content=content)

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Handle unhandled exceptions (catch-all for 500 errors)."""
        request_id = _get_request_id(request)

        logger.error(
            "Unhandled exception occurred",
            extra={
                "request_id": request_id,
                "path": request.url.path,
                "method": request.method,
                "exception_type": type(exc).__name__,
                "exception_message": str(exc),
            },
            exc_info=True,
        )

        if settings.DEBUG:
            error_message = f"Unhandled error: {type(exc).__name__}: {exc!s}"
            details = {"exception_type": type(exc).__name__, "exception_message": f"{exc!s}"}
        else:
            error_message = "An unexpected error occurred. Please try again later."
            details = None

        content: dict[str, Any] = {"error": error_message, "request_id": request_id}
        if details:
            content["details"] = details

        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=content)
