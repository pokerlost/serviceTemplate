"""Public service root router."""

from __future__ import annotations

from fastapi import APIRouter, status
from pypokerlost.types import PokerlostResponse

router = APIRouter(tags=["service"])


@router.get(
    path="/",
    operation_id="getRoot",
    response_model=PokerlostResponse[None],
    status_code=status.HTTP_200_OK,
    summary="Get service root",
    description="Return the minimal service availability response.",
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": PokerlostResponse[None],
        },
    },
)
async def get_service_root() -> dict[str, object]:
    """Return plain data for response-model serialization."""
    return {"ok": True}
