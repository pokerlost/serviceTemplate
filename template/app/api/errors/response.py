"""Universal error response serialization."""

from __future__ import annotations

from fastapi.responses import JSONResponse
from pypokerlost.types import PokerlostResponse


def error_response(
    *,
    status_code: int,
    error: str,
    error_message: str,
) -> JSONResponse:
    """Serialize one validated PokerlostResponse failure."""
    response = PokerlostResponse[None](
        ok=False,
        error=error,
        error_message=error_message,
    )
    return JSONResponse(
        status_code=status_code,
        content=response.model_dump(mode="json"),
    )
