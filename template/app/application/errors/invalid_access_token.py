"""Invalid Pokerlost access-token error."""

from __future__ import annotations

from typing import ClassVar

from .base import ApplicationError


class InvalidAccessTokenError(ApplicationError):
    """The local verifier rejected the supplied access token or audience."""

    error_code: ClassVar[str] = "POKERLOST_ACCESS_TOKEN_INVALID"
    public_message: ClassVar[str] = "Access token is invalid."
