"""Transport-independent application error base."""

from __future__ import annotations

from typing import ClassVar

from service import SERVICE_ERROR_PREFIX


class ApplicationError(Exception):
    """Expected application failure with safe public metadata."""

    error_code: ClassVar[str] = f"{SERVICE_ERROR_PREFIX}_APPLICATION_ERROR"
    public_message: ClassVar[str] = "Application operation failed."
