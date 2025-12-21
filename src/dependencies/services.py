from src.cache.redis import cache
from src.db.db import engine
from src.services.health_service import HealthService


def get_health_service() -> HealthService:
    return HealthService(engine, cache.client)
