"""Invalid application operation error category."""

from __future__ import annotations

from typing import ClassVar

from service import SERVICE_ERROR_PREFIX

from .base import ApplicationError


class InvalidOperationError(ApplicationError):
    """Requested operation is invalid for current state or input semantics."""

    error_code: ClassVar[str] = f"{SERVICE_ERROR_PREFIX}_INVALID_OPERATION"
    public_message: ClassVar[str] = "Operation is invalid."
