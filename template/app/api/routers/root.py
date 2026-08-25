"""Parameterless service root endpoint."""

from __future__ import annotations

from fastapi import APIRouter, status

from api.openapi import OpenAPITag
from api.schemas.responses import ApplicationResponse, RootResponse
from service import SERVICE_NAME

router = APIRouter(tags=[OpenAPITag.SERVICE])


@router.get(
    path="/",
    response_model=RootResponse,
    status_code=status.HTTP_200_OK,
    summary="Get service root",
    description="Return the minimal service availability response.",
    operation_id=f"{SERVICE_NAME}.root",
    openapi_extra={"security": []},
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ApplicationResponse[None],
        },
    },
)
def get_service_root() -> RootResponse:
    """Return the minimal root success contract."""
    return RootResponse(ok=True)
