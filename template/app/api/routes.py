"""Top-level API router registration."""

from __future__ import annotations

from fastapi import FastAPI

from .routers.openapi_document import router as openapi_document_router
from .routers.root import router as root_router


def configure_routes(application: FastAPI) -> None:
    """Register template-managed baseline routers."""
    application.include_router(root_router)
    application.include_router(openapi_document_router)
