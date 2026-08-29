"""Parameterless service root endpoint."""

from __future__ import annotations

from fastapi import APIRouter, status

from api.schemas.responses import ApplicationResponse, RootResponse
from configuration import Settings


def get_service_root() -> RootResponse:
    """Return the minimal root success contract."""
    return RootResponse(ok=True)


def create_root_router(settings: Settings) -> APIRouter:
    """Create the root router from validated runtime settings."""
    router = APIRouter(tags=["service"])
    router.add_api_route(
        path="/",
        endpoint=get_service_root,
        methods=["GET"],
        response_model=RootResponse,
        status_code=status.HTTP_200_OK,
        summary="Get service root",
        description="Return the minimal service availability response.",
        operation_id=settings.root_operation,
        responses={
            status.HTTP_500_INTERNAL_SERVER_ERROR: {
                "model": ApplicationResponse[None],
            },
        },
    )
    return router
