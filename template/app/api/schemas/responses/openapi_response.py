"""Wrapped OpenAPI document response."""

from __future__ import annotations

from api.schemas.json import JSONValue

from .application_response import ApplicationResponse


class OpenAPIResponse(ApplicationResponse[dict[str, JSONValue]]):
    """Canonical envelope containing the generated OpenAPI JSON object."""
