"""Application deployment settings."""

from __future__ import annotations

from pydantic import Field

from .base import SettingsModel
from .environment import Environment


class ApplicationSettings(SettingsModel):
    """Application contract version and deployment environment."""

    version: str = Field(
        default="0.1.0",
        pattern=r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$",
        description="Service contract version exposed through OpenAPI and telemetry.",
    )
    environment: Environment = Field(
        default=Environment.LOCAL,
        description="Current deployment environment.",
    )
