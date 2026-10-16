"""Public, unmodified OpenAPI document for the SDK generator."""

from __future__ import annotations

from fastapi import APIRouter, Request

router = APIRouter(tags=["openapi"])


@router.get("/getOpenApi", operation_id="getOpenApi")
async def getOpenApi(request: Request) -> dict[str, object]:
    """Return FastAPI's actual OpenAPI 3.1 document."""
    document: dict[str, object] = request.app.openapi()
    return document
