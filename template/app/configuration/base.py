"""Immutable base for nested settings groups."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class SettingsModel(BaseModel):
    """Strict immutable nested settings group."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        hide_input_in_errors=True,
        validate_default=True,
    )
