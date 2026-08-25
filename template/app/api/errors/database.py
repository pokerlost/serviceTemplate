"""Database error to HTTP response mapping."""

from __future__ import annotations

import logfire
from fastapi import Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from api.request_context import correlation_id_from_state, request_id_from_state
from service import SERVICE_ERROR_PREFIX

from .response import error_response


class DatabaseUnavailableError(Exception):
    """Required database connectivity is unavailable."""


async def handle_database_unavailable(request: Request, exception: Exception) -> JSONResponse:
    """Return a sanitized dependency-unavailable response."""
    if not isinstance(exception, DatabaseUnavailableError):
        raise TypeError("Unexpected exception registered as DatabaseUnavailableError")
    logfire.warn(
        "PostgreSQL connectivity failed",
        request_id=request_id_from_state(request),
        correlation_id=correlation_id_from_state(request),
        _exc_info=exception,
    )
    return error_response(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        error=f"{SERVICE_ERROR_PREFIX}_DATABASE_UNAVAILABLE",
        error_message="Required database is unavailable",
    )


async def handle_database_error(request: Request, exception: Exception) -> JSONResponse:
    """Sanitize an unexpected SQLAlchemy failure."""
    if not isinstance(exception, SQLAlchemyError):
        raise TypeError("Unexpected exception registered as SQLAlchemyError")
    logfire.error(
        "Database operation failed",
        request_id=request_id_from_state(request),
        correlation_id=correlation_id_from_state(request),
        _exc_info=exception,
    )
    return error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error=f"{SERVICE_ERROR_PREFIX}_DATABASE_ERROR",
        error_message="Database operation failed",
    )
