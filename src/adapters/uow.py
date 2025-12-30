import logging
from typing import Self

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.role_repository import SqlAlchemyRoleRepository
from src.adapters.user_repository import SqlAlchemyUserRepository
from src.core.exceptions.exceptions import ConflictError, ServiceUnavailableError

logger = logging.getLogger(__name__)


class SqlAlchemyUnitOfWork:
    def __init__(
        self,
        session: AsyncSession,
        *,
        users: SqlAlchemyUserRepository,
        roles: SqlAlchemyRoleRepository,
    ) -> None:
        self._session = session
        self.users: SqlAlchemyUserRepository = users
        self.roles: SqlAlchemyRoleRepository = roles

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb,
    ) -> None:
        if exc_type is not None:
            await self.rollback()
            return
        await self.commit()

    async def _rollback_quietly(self, *, context: str) -> None:
        try:
            await self._session.rollback()
        except SQLAlchemyError:
            logger.exception("Rollback failed (%s)", context)

    async def commit(
        self,
        *,
        conflict_message: str = "Conflict occurred",
        unavailable_message: str = "Database commit failed",
    ) -> None:
        try:
            await self._session.commit()
        except IntegrityError as e:
            await self._rollback_quietly(context="after IntegrityError during commit")
            logger.info("IntegrityError during commit", extra={"error": str(e)})
            raise ConflictError(conflict_message) from e
        except SQLAlchemyError as e:
            await self._rollback_quietly(context="after SQLAlchemyError during commit")
            logger.error("SQLAlchemyError during commit", extra={"error": str(e)})
            raise ServiceUnavailableError(unavailable_message) from e

    async def rollback(self) -> None:
        try:
            await self._session.rollback()
        except SQLAlchemyError as e:
            logger.exception("Database rollback failed")
            raise ServiceUnavailableError("Database rollback failed") from e
