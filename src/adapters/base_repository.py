from collections.abc import Sequence
from typing import Any, TypeVar, cast

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.interfaces import ORMOption
from sqlalchemy.sql.elements import ColumnElement

from src.models.base import BaseModel

TModel = TypeVar("TModel", bound=BaseModel)


class SqlAlchemyRepository[TModel]:
    model: type[TModel]

    def __init__(self, session: AsyncSession) -> None:
        if not getattr(type(self), "model", None):
            raise TypeError("Define `model = <Model>` on the subclass to use this repository.")
        self._session = session

    def add(self, obj: TModel) -> None:
        self._session.add(obj)

    async def flush(self) -> None:
        await self._session.flush()

    async def get_by_id(
        self,
        obj_id: int,
        *,
        options: Sequence[ORMOption] = (),
        for_update: bool = False,
        nowait: bool = False,
        skip_locked: bool = False,
    ) -> TModel | None:
        id_col = cast(Any, self.model).id
        return await self.get_one(
            id_col == obj_id,
            options=options,
            for_update=for_update,
            nowait=nowait,
            skip_locked=skip_locked,
        )

    async def get_one(
        self,
        *where_clauses: ColumnElement[bool],
        options: Sequence[ORMOption] = (),
        for_update: bool = False,
        nowait: bool = False,
        skip_locked: bool = False,
    ) -> TModel | None:
        stmt = select(self.model)
        if where_clauses:
            stmt = stmt.where(*where_clauses)
        if options:
            stmt = stmt.options(*options)
        if for_update:
            stmt = stmt.with_for_update(nowait=nowait, skip_locked=skip_locked)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
