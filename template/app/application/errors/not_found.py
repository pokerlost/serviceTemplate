"""Application not-found error category."""

from __future__ import annotations

from typing import ClassVar

from service import SERVICE_ERROR_PREFIX

from .base import ApplicationError


class NotFoundError(ApplicationError):
    """Requested application resource does not exist."""

    error_code: ClassVar[str] = f"{SERVICE_ERROR_PREFIX}_NOT_FOUND"
    public_message: ClassVar[str] = "Requested resource was not found."
