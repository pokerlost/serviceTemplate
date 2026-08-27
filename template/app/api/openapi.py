"""FastAPI-backed OpenAPI publication."""

from __future__ import annotations

from enum import StrEnum
from typing import Final, cast

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from api.schemas.json import JSONValue
from service import SERVICE_NAME

API_DESCRIPTION = "Reusable PokerLost FastAPI service foundation."
OPENAPI_VERSION: Final[str] = "3.1.0"


class OpenAPITag(StrEnum):
    """Baseline OpenAPI route categories."""

    SERVICE = "service"
    OPENAPI = "openapi"


OPENAPI_TAGS = [
    {"name": OpenAPITag.SERVICE, "description": "Service foundation operations."},
    {"name": OpenAPITag.OPENAPI, "description": "Wrapped OpenAPI publication."},
]

type OpenAPISchema = dict[str, JSONValue]


class PokerlostApplication(FastAPI):
    """FastAPI application with minimal PokerLost OpenAPI metadata."""

    def openapi(self) -> OpenAPISchema:
        """Generate and cache the FastAPI schema on first access."""
        if self.openapi_schema is not None:
            return cast(OpenAPISchema, self.openapi_schema)

        schema = cast(
            OpenAPISchema,
            get_openapi(
                title=self.title,
                version=self.version,
                openapi_version=OPENAPI_VERSION,
                description=self.description,
                routes=self.routes,
                tags=OPENAPI_TAGS,
            ),
        )
        schema["x-pokerlost-service"] = {"id": SERVICE_NAME}
        self.openapi_schema = schema
        return schema
