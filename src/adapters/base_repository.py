from collections.abc import Sequence
from typing import Any, TypeVar, cast

from sqlalchemy import delete as sa_delete
from sqlalchemy import func, select
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

    def add_many(self, objs: Sequence[TModel]) -> None:
        self._session.add_all(list(objs))

    async def delete(self, obj: TModel) -> None:
        await self._session.delete(obj)

    async def delete_where(self, *where_clauses: ColumnElement[bool]) -> int:
        stmt = sa_delete(self.model)
        if where_clauses:
            stmt = stmt.where(*where_clauses)
        result = await self._session.execute(stmt)
        rowcount = getattr(result, "rowcount", None)
        return int(rowcount or 0)

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

    async def get_many(
        self,
        *where_clauses: ColumnElement[bool],
        options: Sequence[ORMOption] = (),
        order_by: Sequence[ColumnElement[object]] = (),
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[TModel]:
        stmt = select(self.model)
        if where_clauses:
            stmt = stmt.where(*where_clauses)
        if options:
            stmt = stmt.options(*options)
        if order_by:
            stmt = stmt.order_by(*order_by)
        if limit is not None:
            stmt = stmt.limit(limit)
        if offset is not None:
            stmt = stmt.offset(offset)

        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count(self, *where_clauses: ColumnElement[bool]) -> int:
        stmt = select(func.count()).select_from(self.model)
        if where_clauses:
            stmt = stmt.where(*where_clauses)
        result = await self._session.execute(stmt)
        return int(result.scalar_one())

    async def exists(self, *where_clauses: ColumnElement[bool]) -> bool:
        stmt = select(1).select_from(self.model)
        if where_clauses:
            stmt = stmt.where(*where_clauses)
        stmt = stmt.limit(1)
        result = await self._session.execute(stmt)
        return result.first() is not None
