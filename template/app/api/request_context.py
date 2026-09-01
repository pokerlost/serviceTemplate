"""Server-owned request identifiers for safe observability correlation."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from uuid import uuid4

import logfire
from fastapi import FastAPI, Request, Response


def request_id_from_state(request: Request) -> str:
    """Return the server-generated request identifier."""
    request_id = request.state.request_id
    if not isinstance(request_id, str):
        raise RuntimeError("Request identifier is not initialized")
    return request_id


def configure_request_context(application: FastAPI) -> None:
    """Attach a server-owned identifier without creating a header contract."""
    from .errors.unexpected import handle_unexpected_error

    @application.middleware("http")
    async def request_context_middleware(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        request_id = str(uuid4())
        request.state.request_id = request_id
        with logfire.set_baggage(request_id=request_id):
            try:
                response = await call_next(request)
            except Exception as exception:
                response = await handle_unexpected_error(request, exception)
        return response
