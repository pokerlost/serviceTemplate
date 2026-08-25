"""FastAPI-backed OpenAPI publication."""

from __future__ import annotations

from enum import StrEnum

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from service import SERVICE_NAME

API_DESCRIPTION = "Reusable PokerLost FastAPI service foundation."


class OpenAPITag(StrEnum):
    """Baseline OpenAPI route categories."""

    SERVICE = "service"
    OPENAPI = "openapi"


OPENAPI_TAGS = [
    {"name": OpenAPITag.SERVICE, "description": "Service foundation operations."},
    {"name": OpenAPITag.OPENAPI, "description": "Wrapped OpenAPI publication."},
]

type OpenAPISchema = dict[str, object]


class PokerLostApplication(FastAPI):
    """FastAPI application with minimal PokerLost OpenAPI metadata."""

    def openapi(self) -> OpenAPISchema:
        """Generate and cache the FastAPI schema on first access."""
        if self.openapi_schema is not None:
            return self.openapi_schema

        schema: OpenAPISchema = get_openapi(
            title=self.title,
            version=self.version,
            description=self.description,
            routes=self.routes,
            tags=OPENAPI_TAGS,
        )
        schema["x-pokerlost-service"] = {"id": SERVICE_NAME}
        self.openapi_schema = schema
        return schema
