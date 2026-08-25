"""Wrapped public OpenAPI JSON publication endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Request, status

from api.openapi import OpenAPITag
from api.schemas.responses import ApplicationResponse, OpenApiResponse
from service import SERVICE_NAME

router = APIRouter(tags=[OpenAPITag.OPENAPI])


@router.get(
    path="/openapi.get",
    response_model=OpenApiResponse,
    status_code=status.HTTP_200_OK,
    summary="Get the OpenAPI JSON document",
    description="Return the generated service contract as a wrapped JSON object.",
    operation_id=f"{SERVICE_NAME}.openapi.get",
    openapi_extra={"security": []},
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ApplicationResponse[None],
        },
    },
)
def get_openapi_document(request: Request) -> OpenApiResponse:
    """Return the generated JSON contract inside the universal envelope."""
    return OpenApiResponse(ok=True, result=request.app.openapi())
