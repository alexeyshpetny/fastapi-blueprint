from fastapi import Depends

from src.adapters.uow import SqlAlchemyUnitOfWork
from src.cache.redis import cache_client
from src.db.db import engine
from src.dependencies.adapters import get_uow
from src.services.auth_service import AuthService
from src.services.health_service import HealthService


def get_health_service() -> HealthService:
    return HealthService(engine, cache_client)


async def get_auth_service(
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> AuthService:
    return AuthService(uow=uow)
