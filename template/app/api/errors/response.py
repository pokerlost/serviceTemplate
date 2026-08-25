"""Universal error response serialization."""

from __future__ import annotations

from fastapi.responses import JSONResponse

from api.schemas.responses import ApplicationResponse


def error_response(
    *,
    status_code: int,
    error: str,
    error_message: str,
) -> JSONResponse:
    """Serialize one validated ApplicationResponse failure."""
    response = ApplicationResponse[None](
        ok=False,
        error=error,
        error_message=error_message,
    )
    return JSONResponse(
        status_code=status_code,
        content=response.model_dump(mode="json"),
    )
