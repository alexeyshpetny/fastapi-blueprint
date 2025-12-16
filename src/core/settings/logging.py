import logging

from pydantic import Field
from pydantic_settings import BaseSettings


class LoggingSettings(BaseSettings):
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )

    LOG_FORMAT: str = Field(
        default="json",
        description="Log format: 'json' for structured JSON logs, 'text' for human-readable logs",
    )

    LOG_DATE_FORMAT: str = Field(
        default="%Y-%m-%d %H:%M:%S",
        description="Date format for log timestamps",
    )

    LOG_INCLUDE_REQUEST_ID: bool = Field(
        default=True,
        description="Include request ID (correlation ID) in all log entries",
    )

    LOG_REQUEST_BODY: bool = Field(
        default=False,
        description="Log request body in request/response middleware (WARNING: may log sensitive data)",
    )

    LOG_SLOW_REQUESTS: bool = Field(
        default=True,
        description="Log requests that exceed the slow request threshold",
    )

    LOG_SLOW_REQUEST_THRESHOLD: float = Field(
        default=1.0,
        ge=0.0,
        description="Threshold in seconds for logging slow requests",
    )

    @property
    def log_level_int(self: "LoggingSettings") -> int:
        return getattr(logging, self.LOG_LEVEL.upper(), logging.INFO)
