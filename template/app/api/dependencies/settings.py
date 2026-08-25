"""Application settings dependency."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Request

from configuration import Settings


def _resolve_settings(request: Request) -> Settings:
    """Return settings attached by the application lifespan."""
    settings = request.app.state.settings
    if not isinstance(settings, Settings):
        raise RuntimeError("Application settings are not initialized")
    return settings


type SettingsDep = Annotated[
    Settings,
    Depends(_resolve_settings),
]
