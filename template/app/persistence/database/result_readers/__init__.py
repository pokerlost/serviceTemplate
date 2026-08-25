"""Public SQLAlchemy result reader facade."""

from __future__ import annotations

from .projection import SQLAlchemyProjectionResultReader
from .scalar import SQLAlchemyScalarResultReader

__all__ = (
    "SQLAlchemyProjectionResultReader",
    "SQLAlchemyScalarResultReader",
)
