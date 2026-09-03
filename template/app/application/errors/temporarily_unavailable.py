"""Retryable temporary application availability error."""

from __future__ import annotations

from math import isfinite
from typing import ClassVar

from service import SERVICE_ERROR_PREFIX

from .base import ApplicationError


class TemporarilyUnavailableError(ApplicationError):
    """A retryable dependency or application capability is temporarily unavailable."""

    error_code: ClassVar[str] = f"{SERVICE_ERROR_PREFIX}_TEMPORARILY_UNAVAILABLE"
    public_message: ClassVar[str] = "Required capability is temporarily unavailable."

    def __init__(self, *, retry_after: float | None = None) -> None:
        if retry_after is not None and (not isfinite(retry_after) or retry_after < 0.0):
            raise ValueError("retry_after must be finite and non-negative")
        super().__init__(self.public_message)
        self._retry_after = retry_after

    @property
    def retry_after(self) -> float | None:
        """Return the validated delay in seconds when one is available."""
        return self._retry_after
