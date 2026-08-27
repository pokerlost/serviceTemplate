"""Per-request identifiers and safe observability propagation."""

from __future__ import annotations

import re
from collections.abc import Awaitable, Callable
from uuid import uuid4

import logfire
from fastapi import FastAPI, Request, Response

REQUEST_ID_HEADER = "X-Request-ID"
CORRELATION_ID_HEADER = "X-Correlation-ID"
_CORRELATION_ID_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:/-]{0,127}\Z")


def request_id_from_state(request: Request) -> str:
    """Return the server-generated request identifier."""
    request_id = request.state.request_id
    if not isinstance(request_id, str):
        raise RuntimeError("Request identifier is not initialized")
    return request_id


def correlation_id_from_state(request: Request) -> str:
    """Return the validated correlation identifier."""
    correlation_id = request.state.correlation_id
    if not isinstance(correlation_id, str):
        raise RuntimeError("Correlation identifier is not initialized")
    return correlation_id


def _resolve_correlation_id(request: Request) -> str:
    supplied_id = request.headers.get(CORRELATION_ID_HEADER)
    if supplied_id is not None and _CORRELATION_ID_PATTERN.fullmatch(supplied_id):
        return supplied_id
    return str(uuid4())


def configure_request_context(application: FastAPI) -> None:
    """Attach server-owned identifiers and response headers."""
    from .errors.unexpected import handle_unexpected_error

    @application.middleware("http")
    async def request_context_middleware(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        request_id = str(uuid4())
        correlation_id = _resolve_correlation_id(request)
        request.state.request_id = request_id
        request.state.correlation_id = correlation_id
        with logfire.set_baggage(request_id=request_id, correlation_id=correlation_id):
            try:
                response = await call_next(request)
            except Exception as exception:
                response = await handle_unexpected_error(request, exception)
        response.headers[REQUEST_ID_HEADER] = request_id
        response.headers[CORRELATION_ID_HEADER] = correlation_id
        return response
