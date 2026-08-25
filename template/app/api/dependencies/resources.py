"""Runtime resource dependency."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Request

from api.resources import ApplicationResources


def _resolve_application_resources(request: Request) -> ApplicationResources:
    """Return lifespan-owned application resources."""
    resources = request.app.state.resources
    if not isinstance(resources, ApplicationResources):
        raise RuntimeError("Application resources are not initialized")
    return resources


type ApplicationResourcesDep = Annotated[
    ApplicationResources,
    Depends(_resolve_application_resources),
]
