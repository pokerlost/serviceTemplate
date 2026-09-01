"""Wrapped public OpenAPI JSON publication router."""

from __future__ import annotations

from fastapi import APIRouter, FastAPI, status
from pypokerlost.types import APIOperation

from api.schemas.responses import ApplicationResponse, OpenAPIResponse


def create_openapi_document_router(
    *,
    application: FastAPI,
    operation: APIOperation,
) -> APIRouter:
    """Create the publication router from validated runtime settings."""
    router = APIRouter(tags=["openapi"])

    @router.get(
        path=f"/{operation}",
        operation_id=operation,
        response_model=OpenAPIResponse,
        status_code=status.HTTP_200_OK,
        summary="Get the OpenAPI JSON document",
        description="Return the generated service contract as a wrapped JSON object.",
        responses={
            status.HTTP_500_INTERNAL_SERVER_ERROR: {
                "model": ApplicationResponse[None],
            },
        },
    )
    async def get_openapi_document() -> OpenAPIResponse:
        """Return the generated JSON contract inside the universal envelope."""
        return OpenAPIResponse(ok=True, result=application.openapi())

    return router
