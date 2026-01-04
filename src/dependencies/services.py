from fastapi import Depends

from src.adapters.role_repository import SqlAlchemyRoleRepository
from src.adapters.user_repository import SqlAlchemyUserRepository
from src.cache.redis import cache_client
from src.db.db import engine
from src.dependencies.adapters import get_roles_repository, get_users_repository
from src.services.auth_service import AuthService
from src.services.health_service import HealthService


def get_health_service() -> HealthService:
    return HealthService(engine, cache_client)


async def get_auth_service(
    users: SqlAlchemyUserRepository = Depends(get_users_repository),
    roles: SqlAlchemyRoleRepository = Depends(get_roles_repository),
) -> AuthService:
    return AuthService(users=users, roles=roles)
