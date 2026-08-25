"""Application integrity error category."""

from __future__ import annotations

from typing import ClassVar

from service import SERVICE_ERROR_PREFIX

from .base import ApplicationError


class IntegrityError(ApplicationError):
    """Application state violates a required invariant."""

    error_code: ClassVar[str] = f"{SERVICE_ERROR_PREFIX}_INTEGRITY_ERROR"
    public_message: ClassVar[str] = "Application state is inconsistent."
