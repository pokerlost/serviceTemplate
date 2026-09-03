"""Insufficient Pokerlost scope error."""

from __future__ import annotations

from typing import ClassVar

from .base import ApplicationError


class InsufficientScopeError(ApplicationError):
    """The verified token lacks one or more exact route scopes."""

    error_code: ClassVar[str] = "POKERLOST_INSUFFICIENT_SCOPE"
    public_message: ClassVar[str] = "Access token does not grant the required scope."
