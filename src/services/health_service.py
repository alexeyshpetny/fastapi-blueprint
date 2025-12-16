import logging
from typing import Any

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine

from src.core.settings import settings

logger = logging.getLogger(__name__)


class HealthService:
    def __init__(self, engine: AsyncEngine) -> None:
        self.engine = engine
        self.service_name = "shpetny-fastapi-blueprint"
        self.version = settings.DOC_VERSION

    async def check_liveness(self) -> dict[str, str]:
        """Check if the service is alive."""
        logger.debug("Liveness check requested")
        return {
            "status": "alive",
            "service": self.service_name,
            "version": self.version,
        }

    async def check_readiness(self) -> dict[str, Any]:
        """Check if the service is ready, including database connectivity."""
        logger.debug("Readiness check requested")
        checks = {}
        all_healthy = True
        error_message: str | None = None

        try:
            async with self.engine.connect() as connection:
                await connection.execute(text("SELECT 1"))
                checks["database"] = "ok"
        except SQLAlchemyError as e:
            logger.warning("Database health check failed", extra={"error": str(e)})
            checks["database"] = "error"
            all_healthy = False
            error_message = f"Database connection failed: {e!s}"
        except Exception as e:
            logger.error("Unexpected error during database health check", exc_info=True)
            checks["database"] = "error"
            all_healthy = False
            error_message = f"Unexpected error: {e!s}"

        response_data = {
            "status": "ready" if all_healthy else "not_ready",
            "service": self.service_name,
            "version": self.version,
            "checks": checks,
        }

        if not all_healthy:
            response_data["error"] = error_message

        return response_data
