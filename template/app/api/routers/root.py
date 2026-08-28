"""Parameterless service root endpoint."""

from __future__ import annotations

from typing import Final

from fastapi import APIRouter, status

from api.schemas.responses import ApplicationResponse, RootResponse
from service import SERVICE_SLUG

router = APIRouter(tags=["service"])
ROOT_OPERATION: Final[str] = f"{SERVICE_SLUG}.root"


@router.get(
    path="/",
    response_model=RootResponse,
    status_code=status.HTTP_200_OK,
    summary="Get service root",
    description="Return the minimal service availability response.",
    operation_id=ROOT_OPERATION,
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ApplicationResponse[None],
        },
    },
)
def get_service_root() -> RootResponse:
    """Return the minimal root success contract."""
    return RootResponse(ok=True)
