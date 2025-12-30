from sqlalchemy.orm import selectinload

from src.adapters.base_repository import SqlAlchemyRepository
from src.models.user import User


class SqlAlchemyUserRepository(SqlAlchemyRepository[User]):
    model = User

    async def get_by_email(self, email: str) -> User | None:
        return await self.get_one(
            User.email == email,
            options=[selectinload(User.roles)],
        )
