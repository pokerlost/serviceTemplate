"""Small shared base for UUID SQLAlchemy repository adapters."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.selectable import TypedReturnsRows

from persistence.database import UUIDModel
from persistence.database.result_readers import (
    SQLAlchemyProjectionResultReader,
    SQLAlchemyScalarResultReader,
)
from persistence.projections import Projection


class SQLAlchemyRepository:
    """Own one request session and typed SQLAlchemy result execution."""

    __slots__ = ("_session",)

    def __init__(self, session: AsyncSession) -> None:
        """Store the request-scoped SQLAlchemy session."""
        self._session = session

    async def _read_scalar[ResultT](
        self,
        statement: TypedReturnsRows[tuple[ResultT]],
    ) -> SQLAlchemyScalarResultReader[ResultT]:
        result = await self._session.execute(statement)
        return SQLAlchemyScalarResultReader(result)

    async def _read_projection[ProjectionT: Projection, *RowT](
        self,
        statement: TypedReturnsRows[tuple[*RowT]],
        projection_type: type[ProjectionT],
    ) -> SQLAlchemyProjectionResultReader[ProjectionT]:
        result = await self._session.execute(statement)
        return SQLAlchemyProjectionResultReader(result, projection_type)


class SQLAlchemyEntityRepository[ModelT: UUIDModel](SQLAlchemyRepository):
    """Provide common UUID lookup for a standard persisted entity."""

    model: type[ModelT]

    async def get_by_id(
        self,
        model_id: UUID,
    ) -> ModelT | None:
        """Return one standard UUID entity when it exists."""
        result = await self._read_scalar(
            select(self.model).where(self.model.id == model_id),
        )
        return result.one_or_none()
