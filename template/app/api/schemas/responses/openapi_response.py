"""Wrapped OpenAPI document response."""

from __future__ import annotations

from .application_response import ApplicationResponse


class OpenApiResponse(ApplicationResponse[dict[str, object]]):
    """Canonical envelope containing the generated OpenAPI JSON object."""
