import logging

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from src.adapters.base_repository import SqlAlchemyRepository
from src.auth.exceptions import UserAlreadyExistsError
from src.models.user import User

logger = logging.getLogger(__name__)


class SqlAlchemyUserRepository(SqlAlchemyRepository[User]):
    model = User

    async def get_by_email(self, email: str) -> User | None:
        return await self.get_one(
            User.email == email,
            options=[selectinload(User.roles)],
        )

    async def flush(self) -> None:
        await super().flush()

    async def safe_flush(self, user: User) -> None:
        try:
            await super().flush()
        except IntegrityError as e:
            logger.warning(
                "Database integrity error during user creation",
                extra={"error": str(e)},
            )
            raise UserAlreadyExistsError() from None
