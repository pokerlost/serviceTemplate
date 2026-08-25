"""Typed scalar extraction from SQLAlchemy execution results."""

from __future__ import annotations

from sqlalchemy.engine import Result


class SQLAlchemyScalarResultReader[ResultT]:
    """Read typed scalar values from one SQLAlchemy execution result."""

    def __init__(self, result: Result[tuple[ResultT]]) -> None:
        """Wrap one typed SQLAlchemy scalar result."""
        self._result = result

    def one(self) -> ResultT:
        """Return exactly one scalar value."""
        return self._result.scalar_one()

    def one_or_none(self) -> ResultT | None:
        """Return zero or one scalar value."""
        return self._result.scalar_one_or_none()

    def all(self) -> list[ResultT]:
        """Materialize every scalar value in result order."""
        return list(self._result.scalars().all())
