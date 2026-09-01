"""Parameterless service root router."""

from __future__ import annotations

from fastapi import APIRouter, status
from pypokerlost.types import APIOperation

from api.schemas.responses import ApplicationResponse, RootResponse


def create_root_router(*, operation: APIOperation) -> APIRouter:
    """Create the root router from validated runtime settings."""
    router = APIRouter(tags=["service"])

    @router.get(
        path="/",
        operation_id=operation,
        response_model=RootResponse,
        status_code=status.HTTP_200_OK,
        summary="Get service root",
        description="Return the minimal service availability response.",
        responses={
            status.HTTP_500_INTERNAL_SERVER_ERROR: {
                "model": ApplicationResponse[None],
            },
        },
    )
    async def get_service_root() -> RootResponse:
        """Return the minimal root success contract."""
        return RootResponse(ok=True)

    return router
