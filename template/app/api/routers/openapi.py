"""Public OpenAPI JSON publication router."""

from __future__ import annotations

from typing import cast

from fastapi import APIRouter, FastAPI, status
from pypokerlost.types import PokerlostOperation, PokerlostResponse

from api.schemas.json import JSONValue


def create_openapi_router(
    *,
    application: FastAPI,
    operation: PokerlostOperation,
) -> APIRouter:
    """Create the bodyless OpenAPI publication router."""
    router = APIRouter(tags=["openapi"])

    @router.get(
        path=f"/{operation}",
        operation_id=operation,
        response_model=PokerlostResponse[dict[str, JSONValue]],
        status_code=status.HTTP_200_OK,
        summary="Get the OpenAPI JSON document",
        description="Return the generated service contract in the canonical response envelope.",
        responses={
            status.HTTP_500_INTERNAL_SERVER_ERROR: {
                "model": PokerlostResponse[None],
            },
        },
    )
    async def get_openapi_document() -> PokerlostResponse[dict[str, JSONValue]]:
        """Return the unmodified FastAPI OpenAPI document."""
        document = cast(dict[str, JSONValue], application.openapi())
        return PokerlostResponse[dict[str, JSONValue]](ok=True, result=document)

    return router
