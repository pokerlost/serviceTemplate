"""Service root response."""

from __future__ import annotations

from .application_response import ApplicationResponse


class RootResponse(ApplicationResponse[None]):
    """Canonical successful root envelope."""
