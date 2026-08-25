"""Transport-independent application error facade."""

from __future__ import annotations

from .base import ApplicationError
from .conflict import ConflictError
from .integrity import IntegrityError
from .invalid_operation import InvalidOperationError
from .not_found import NotFoundError

__all__ = (
    "ApplicationError",
    "ConflictError",
    "IntegrityError",
    "InvalidOperationError",
    "NotFoundError",
)
