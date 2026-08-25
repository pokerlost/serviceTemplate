"""Logfire runtime settings."""

from __future__ import annotations

from typing import Self

from logfire import LevelName
from pydantic import Field, SecretStr, model_validator

from .base import SettingsModel


class LogfireSettings(SettingsModel):
    """Single observability backend configuration."""

    enabled: bool = Field(default=True, description="Enable Logfire instrumentation.")
    send_to_logfire: bool = Field(
        default=False,
        description="Send telemetry to the configured Logfire project.",
    )
    console: bool = Field(default=True, description="Render telemetry to the process console.")
    minimum_level: LevelName = Field(default="info", description="Minimum record level.")
    token: SecretStr | None = Field(
        default=None,
        description="Logfire project write token required for remote delivery.",
        repr=False,
    )

    @model_validator(mode="after")
    def validate_remote_delivery(self) -> Self:
        """Require an explicit secret whenever remote delivery is enabled."""
        if self.enabled and self.send_to_logfire and self.token is None:
            raise ValueError("Logfire token is required when remote delivery is enabled")
        return self
