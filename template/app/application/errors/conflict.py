"""Application conflict error category."""

from __future__ import annotations

from typing import ClassVar

from service import SERVICE_ERROR_PREFIX

from .base import ApplicationError


class ConflictError(ApplicationError):
    """Current state conflicts with the requested operation."""

    error_code: ClassVar[str] = f"{SERVICE_ERROR_PREFIX}_CONFLICT"
    public_message: ClassVar[str] = "Operation conflicts with current state."
