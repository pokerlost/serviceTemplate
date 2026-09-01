"""Missing Pokerlost request authentication error."""

from __future__ import annotations

from typing import ClassVar

from .base import ApplicationError


class AuthenticationRequiredError(ApplicationError):
    """The request omitted or malformed its body authorization object."""

    error_code: ClassVar[str] = "AUTHENTICATION_REQUIRED"
    public_message: ClassVar[str] = "Authentication is required."
