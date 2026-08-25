"""Framework HTTP error normalization."""

from __future__ import annotations

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from service import SERVICE_ERROR_PREFIX

from .response import error_response


async def handle_http_error(_request: Request, exception: Exception) -> JSONResponse:
    """Replace framework detail responses with the universal safe error envelope."""
    if not isinstance(exception, StarletteHTTPException):
        raise TypeError("Unexpected exception registered as HTTPException")
    if exception.status_code == status.HTTP_404_NOT_FOUND:
        error = f"{SERVICE_ERROR_PREFIX}_NOT_FOUND"
        message = "Resource not found"
    elif exception.status_code == status.HTTP_405_METHOD_NOT_ALLOWED:
        error = f"{SERVICE_ERROR_PREFIX}_METHOD_NOT_ALLOWED"
        message = "Method not allowed"
    else:
        error = f"{SERVICE_ERROR_PREFIX}_HTTP_ERROR"
        message = "HTTP request failed"
    return error_response(
        status_code=exception.status_code,
        error=error,
        error_message=message,
    )
