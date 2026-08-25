"""Typed projection extraction from SQLAlchemy mapping results."""

from __future__ import annotations

from sqlalchemy.engine import MappingResult, Result, RowMapping

from persistence.projections import Projection


def _projection_values(row: RowMapping) -> dict[str, object]:
    """Copy one labeled SQLAlchemy row into a transport-independent mapping."""
    values: dict[str, object] = {}
    for key, value in row.items():
        if not isinstance(key, str):
            raise TypeError("Projection queries must label every selected value")
        values[key] = value
    return values


class SQLAlchemyProjectionResultReader[ProjectionT: Projection]:
    """Materialize labeled SQLAlchemy mappings into typed read projections."""

    def __init__[*RowT](
        self,
        result: Result[tuple[*RowT]],
        projection_type: type[ProjectionT],
    ) -> None:
        """Keep one mapping result and its target projection type."""
        self._result: MappingResult = result.mappings()
        self._projection_type = projection_type

    def one(self) -> ProjectionT:
        """Return exactly one materialized projection."""
        return self._projection_type.from_mapping(_projection_values(self._result.one()))

    def one_or_none(self) -> ProjectionT | None:
        """Return zero or one materialized projection."""
        row = self._result.one_or_none()
        if row is None:
            return None
        return self._projection_type.from_mapping(_projection_values(row))

    def all(self) -> list[ProjectionT]:
        """Materialize every projection in result order."""
        return [
            self._projection_type.from_mapping(_projection_values(row))
            for row in self._result.all()
        ]
