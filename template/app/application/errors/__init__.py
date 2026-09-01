"""Transport-independent application error facade."""

from __future__ import annotations

from .authentication_required import AuthenticationRequiredError
from .base import ApplicationError
from .conflict import ConflictError
from .insufficient_scope import InsufficientScopeError
from .integrity import IntegrityError
from .invalid_access_token import InvalidAccessTokenError
from .invalid_operation import InvalidOperationError
from .not_found import NotFoundError

__all__ = (
    "ApplicationError",
    "AuthenticationRequiredError",
    "ConflictError",
    "InsufficientScopeError",
    "IntegrityError",
    "InvalidAccessTokenError",
    "InvalidOperationError",
    "NotFoundError",
)
