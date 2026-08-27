"""Wrapped public OpenAPI JSON publication endpoint."""

from __future__ import annotations

from typing import Final

from fastapi import APIRouter, Request, status

from api.openapi import OpenAPITag
from api.schemas.responses import ApplicationResponse, OpenAPIResponse

router = APIRouter(tags=[OpenAPITag.OPENAPI])
OPENAPI_OPERATION: Final[str] = "openapi.get"


@router.get(
    path=f"/{OPENAPI_OPERATION}",
    response_model=OpenAPIResponse,
    status_code=status.HTTP_200_OK,
    summary="Get the OpenAPI JSON document",
    description="Return the generated service contract as a wrapped JSON object.",
    operation_id=OPENAPI_OPERATION,
    openapi_extra={"security": []},
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ApplicationResponse[None],
        },
    },
)
def get_openapi_document(request: Request) -> OpenAPIResponse:
    """Return the generated JSON contract inside the universal envelope."""
    return OpenAPIResponse(ok=True, result=request.app.openapi())
