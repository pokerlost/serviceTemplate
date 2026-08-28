"""FastAPI-backed OpenAPI publication."""

from __future__ import annotations

from typing import cast

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from api.schemas.json import JSONValue
from service import SERVICE_NAME

type OpenAPISchema = dict[str, JSONValue]


class PokerlostApplication(FastAPI):
    """FastAPI application with minimal PokerLost OpenAPI metadata."""

    def openapi(self) -> OpenAPISchema:
        """Generate and cache the FastAPI schema on first access."""
        if self.openapi_schema is None:
            schema = cast(
                OpenAPISchema,
                get_openapi(
                    title=self.title,
                    version=self.version,
                    routes=self.routes,
                ),
            )
            schema["x-pokerlost-service"] = {"id": SERVICE_NAME}
            self.openapi_schema = schema
        return cast(OpenAPISchema, self.openapi_schema)
