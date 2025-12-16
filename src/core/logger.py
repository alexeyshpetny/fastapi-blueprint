import logging
import sys
from contextvars import ContextVar

from pythonjsonlogger import jsonlogger

from src.core.settings import settings

request_id_context: ContextVar[str | None] = ContextVar("request_id", default=None)


class RequestIDFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        request_id = request_id_context.get()
        record.request_id = request_id or "-"
        return True


def setup_logging() -> None:
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.log_level_int)
    root_logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(settings.log_level_int)

    if settings.LOG_FORMAT.lower() == "json":
        formatter: logging.Formatter = jsonlogger.JsonFormatter(
            fmt="%(asctime)s %(name)s %(levelname)s %(message)s %(pathname)s %(lineno)d",
            datefmt=settings.LOG_DATE_FORMAT,
            json_ensure_ascii=False,
        )
    else:
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)-8s] [%(name)s] [%(request_id)s] %(message)s",
            datefmt=settings.LOG_DATE_FORMAT,
        )

    handler.setFormatter(formatter)

    if settings.LOG_INCLUDE_REQUEST_ID:
        handler.addFilter(RequestIDFilter())

    root_logger.addHandler(handler)

    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    sqlalchemy_level = logging.INFO if settings.DB_ECHO else logging.WARNING
    logging.getLogger("sqlalchemy.engine").setLevel(sqlalchemy_level)
