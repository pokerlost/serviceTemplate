"""Application error to HTTP response mapping."""

from __future__ import annotations

import logfire
from fastapi import Request, status
from fastapi.responses import JSONResponse

from api.request_context import correlation_id_from_state, request_id_from_state
from application.errors import (
    ApplicationError,
    ConflictError,
    IntegrityError,
    InvalidOperationError,
    NotFoundError,
)

from .response import error_response


async def handle_application_error(request: Request, exception: Exception) -> JSONResponse:
    """Map a semantic application failure without exposing internal state."""
    if not isinstance(exception, ApplicationError):
        raise TypeError("Unexpected exception registered as ApplicationError")
    if isinstance(exception, NotFoundError):
        status_code = status.HTTP_404_NOT_FOUND
    elif isinstance(exception, ConflictError):
        status_code = status.HTTP_409_CONFLICT
    elif isinstance(exception, InvalidOperationError):
        status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    elif isinstance(exception, IntegrityError):
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    else:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    if status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
        logfire.error(
            "Application operation failed",
            request_id=request_id_from_state(request),
            correlation_id=correlation_id_from_state(request),
            _exc_info=exception,
        )
    return error_response(
        status_code=status_code,
        error=exception.error_code,
        error_message=exception.public_message,
    )
