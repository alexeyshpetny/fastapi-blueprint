import logging
from typing import Any

from redis.asyncio import Redis
from redis.exceptions import RedisError
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine

from src.core.settings import settings

logger = logging.getLogger(__name__)


class HealthService:
    def __init__(self, engine: AsyncEngine, cache_client: Redis | None = None) -> None:
        self.engine = engine
        self.cache_client = cache_client
        self.service_name = settings.SERVICE_NAME
        self.version = settings.DOC_VERSION

    async def check_liveness(self) -> dict[str, str]:
        logger.debug("Liveness check requested")
        return {
            "status": "alive",
            "service": self.service_name,
            "version": self.version,
        }

    async def check_readiness(self) -> dict[str, Any]:
        logger.debug("Readiness check requested")
        checks: dict[str, str] = {}
        errors: list[str] = []

        await self._check_database(checks, errors)
        if settings.CACHE_ENABLED:
            await self._check_cache(checks, errors)

        all_healthy = len(errors) == 0
        response_data = {
            "status": "ready" if all_healthy else "not_ready",
            "service": self.service_name,
            "version": self.version,
            "checks": checks,
        }
        if not all_healthy:
            response_data["error"] = "; ".join(errors)

        return response_data

    async def _check_database(self, checks: dict[str, str], errors: list[str]) -> None:
        try:
            async with self.engine.connect() as connection:
                await connection.execute(text("SELECT 1"))
                checks["database"] = "ok"
        except SQLAlchemyError as e:
            logger.warning("Database readiness check failed", extra={"error": str(e)})
            checks["database"] = "error"
            errors.append(f"Database connection failed: {e!s}")
        except Exception as e:
            logger.error("Unexpected error during database readiness check", exc_info=True)
            checks["database"] = "error"
            errors.append(f"Database error: {e!s}")

    async def _check_cache(self, checks: dict[str, str], errors: list[str]) -> None:
        try:
            if self.cache_client is None:
                checks["cache"] = "disabled"
                return

            await self.cache_client.ping()
            checks["cache"] = "ok"
        except RedisError as e:
            logger.warning("Cache readiness check failed", extra={"error": str(e)})
            checks["cache"] = "error"
            errors.append(f"Cache connection failed: {e!s}")
        except Exception as e:
            logger.error("Unexpected error during cache readiness check", exc_info=True)
            checks["cache"] = "error"
            errors.append(f"Cache error: {e!s}")
