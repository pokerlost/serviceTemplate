"""Expired Pokerlost access-token error."""

from __future__ import annotations

from typing import ClassVar

from .base import ApplicationError


class AccessTokenExpiredError(ApplicationError):
    """The supplied access token expired before endpoint execution."""

    error_code: ClassVar[str] = "POKERLOST_ACCESS_TOKEN_EXPIRED"
    public_message: ClassVar[str] = "The access token has expired."
