from collections.abc import AsyncIterator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.role_repository import SqlAlchemyRoleRepository
from src.adapters.uow import SqlAlchemyUnitOfWork
from src.adapters.user_repository import SqlAlchemyUserRepository
from src.cache.redis import cache_client
from src.db.db import engine, get_session
from src.services.auth_service import AuthService
from src.services.health_service import HealthService


async def get_users_repository(
    session: AsyncSession = Depends(get_session),
) -> SqlAlchemyUserRepository:
    return SqlAlchemyUserRepository(session=session)


async def get_roles_repository(
    session: AsyncSession = Depends(get_session),
) -> SqlAlchemyRoleRepository:
    return SqlAlchemyRoleRepository(session=session)


async def get_uow(
    session: AsyncSession = Depends(get_session),
    users: SqlAlchemyUserRepository = Depends(get_users_repository),
    roles: SqlAlchemyRoleRepository = Depends(get_roles_repository),
) -> AsyncIterator[SqlAlchemyUnitOfWork]:
    async with SqlAlchemyUnitOfWork(session, users=users, roles=roles) as uow:
        yield uow


def get_health_service() -> HealthService:
    return HealthService(engine, cache_client)


async def get_auth_service(
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> AuthService:
    return AuthService(uow=uow)
