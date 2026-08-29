"""Wrapped public OpenAPI JSON publication endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Request, status

from api.schemas.responses import ApplicationResponse, OpenAPIResponse
from configuration import Settings


def get_openapi_document(request: Request) -> OpenAPIResponse:
    """Return the generated JSON contract inside the universal envelope."""
    return OpenAPIResponse(ok=True, result=request.app.openapi())


def create_openapi_document_router(settings: Settings) -> APIRouter:
    """Create the publication router from validated runtime settings."""
    router = APIRouter(tags=["openapi"])
    router.add_api_route(
        path=f"/{settings.openapi_operation}",
        endpoint=get_openapi_document,
        methods=["GET"],
        response_model=OpenAPIResponse,
        status_code=status.HTTP_200_OK,
        summary="Get the OpenAPI JSON document",
        description="Return the generated service contract as a wrapped JSON object.",
        operation_id=settings.openapi_operation,
        responses={
            status.HTTP_500_INTERNAL_SERVER_ERROR: {
                "model": ApplicationResponse[None],
            },
        },
    )
    return router
