from collections.abc import AsyncIterator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.role_repository import SqlAlchemyRoleRepository
from src.adapters.uow import SqlAlchemyUnitOfWork
from src.adapters.user_repository import SqlAlchemyUserRepository
from src.db.db import get_session


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
