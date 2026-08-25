"""Request validation error to HTTP response mapping."""

from __future__ import annotations

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from service import SERVICE_ERROR_PREFIX

from .response import error_response


async def handle_validation_error(_request: Request, exception: Exception) -> JSONResponse:
    """Return a stable validation failure without echoing submitted values."""
    if not isinstance(exception, RequestValidationError):
        raise TypeError("Unexpected exception registered as RequestValidationError")
    return error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        error=f"{SERVICE_ERROR_PREFIX}_VALIDATION_ERROR",
        error_message="Request validation failed",
    )
