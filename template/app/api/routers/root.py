"""Parameterless service root router."""

from __future__ import annotations

from fastapi import APIRouter, status
from pypokerlost.types import PokerlostOperation, PokerlostResponse


def create_root_router(*, operation: PokerlostOperation) -> APIRouter:
    """Create the root router from validated runtime settings."""
    router = APIRouter(tags=["service"])

    @router.get(
        path="/",
        operation_id=operation,
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
    async def get_service_root() -> PokerlostResponse[None]:
        """Return the minimal root success contract."""
        return PokerlostResponse[None](ok=True)

    return router
