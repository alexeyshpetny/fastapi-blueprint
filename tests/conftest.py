from collections.abc import AsyncIterator

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from src.adapters.role_repository import SqlAlchemyRoleRepository
from src.adapters.user_repository import SqlAlchemyUserRepository
from src.core.logger import request_id_context
from src.core.settings import Settings
from src.main import create_app
from src.models.base import Base
from src.models.user import User
from src.services.auth_service import AuthService


@pytest.fixture(autouse=True)
def clear_request_context():
    yield
    request_id_context.set(None)


@pytest.fixture
def settings() -> Settings:
    return Settings()


@pytest.fixture
def engine(settings: Settings) -> AsyncEngine:
    return create_async_engine(
        settings.db_url,
        poolclass=NullPool,
        echo=settings.DB_ECHO,
    )


@pytest.fixture
def async_session_maker(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, expire_on_commit=False)


@pytest.fixture
async def session(
    async_session_maker: async_sessionmaker[AsyncSession],
) -> AsyncIterator[AsyncSession]:
    async with async_session_maker() as session:
        yield session


@pytest.fixture(autouse=True)
async def restart_db(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest.fixture
def users_repository(session: AsyncSession) -> SqlAlchemyUserRepository:
    return SqlAlchemyUserRepository(session=session)


@pytest.fixture
def roles_repository(session: AsyncSession) -> SqlAlchemyRoleRepository:
    return SqlAlchemyRoleRepository(session=session)


@pytest.fixture
def auth_service(
    users_repository: SqlAlchemyUserRepository,
    roles_repository: SqlAlchemyRoleRepository,
) -> AuthService:
    return AuthService(users=users_repository, roles=roles_repository)


@pytest.fixture
async def user_factory(
    auth_service: AuthService,
    roles_repository: SqlAlchemyRoleRepository,
    session: AsyncSession,
):
    async def _create_user(
        email: str,
        password: str = "TestPassword123!",
        username: str | None = None,
        is_active: bool = True,
        roles: list[str] | None = None,
    ) -> User:
        user = await auth_service.create_user(email=email, password=password, username=username)

        if not is_active:
            user.is_active = False
        if roles:
            for role_name in roles:
                role = await roles_repository.get_or_create(name=role_name, description=f"{role_name} role")
                if role not in user.roles:
                    user.roles.append(role)

        await session.commit()
        return user

    return _create_user


@pytest.fixture
async def app(session: AsyncSession) -> FastAPI:
    from src.db.db import get_session

    app = create_app()

    async def override_get_session() -> AsyncIterator[AsyncSession]:
        yield session

    app.dependency_overrides[get_session] = override_get_session
    return app


@pytest.fixture
async def client(app) -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
