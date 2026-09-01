"""Shared SQLAlchemy repository execution base."""

from __future__ import annotations

from sqlalchemy.engine import ScalarResult
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.selectable import TypedReturnsRows


class SQLAlchemyRepository:
    """Own one request session and typed SQLAlchemy result execution."""

    __slots__ = ("_session",)

    def __init__(self, session: AsyncSession) -> None:
        """Store the request-scoped SQLAlchemy session."""
        self._session = session

    async def _read_scalar[ResultT](
        self,
        statement: TypedReturnsRows[tuple[ResultT]],
    ) -> ScalarResult[ResultT]:
        result = await self._session.execute(statement)
        return result.scalars()
