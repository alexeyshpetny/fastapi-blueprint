from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from src.adapters.base_repository import SqlAlchemyRepository
from src.core.exceptions.exceptions import ServiceUnavailableError
from src.models.role import Role


class SqlAlchemyRoleRepository(SqlAlchemyRepository[Role]):
    model = Role

    async def get_by_name(self, name: str) -> Role | None:
        return await self.get_one(Role.name == name)

    async def get_or_create(self, *, name: str, description: str | None) -> Role:
        existing = await self.get_by_name(name)
        if existing is not None:
            return existing

        role = Role(name=name, description=description)
        self.add(role)

        try:
            async with self._session.begin_nested():
                await self._session.flush()
            return role
        except IntegrityError as e:
            existing = await self.get_by_name(name)
            if existing is None:
                raise ServiceUnavailableError("Role creation failed") from e
            return existing
        except SQLAlchemyError as e:
            raise ServiceUnavailableError("Database error during role creation") from e
