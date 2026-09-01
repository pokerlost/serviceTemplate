"""Unexpected exception to HTTP response mapping."""

from __future__ import annotations

import logfire
from fastapi import Request, status
from fastapi.responses import JSONResponse

from api.request_context import request_id_from_state
from service import SERVICE_ERROR_PREFIX

from .response import error_response


async def handle_unexpected_error(request: Request, exception: Exception) -> JSONResponse:
    """Record an unexpected exception and return a safe public failure."""
    request_id = request_id_from_state(request)
    logfire.error(
        "Unhandled application error",
        request_id=request_id,
        _exc_info=exception,
    )
    return error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error=f"{SERVICE_ERROR_PREFIX}_INTERNAL_ERROR",
        error_message="Internal server error",
    )
