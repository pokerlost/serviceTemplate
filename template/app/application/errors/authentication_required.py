"""Missing Pokerlost request authentication error."""

from __future__ import annotations

from typing import ClassVar

from .base import ApplicationError


class AuthenticationRequiredError(ApplicationError):
    """The request omitted or malformed its bearer authorization header."""

    error_code: ClassVar[str] = "POKERLOST_AUTHENTICATION_REQUIRED"
    public_message: ClassVar[str] = "Authentication is required."
