"""Global immutable service settings."""

from __future__ import annotations

from typing import Self

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from pypokerlost.types import PokerlostOperation

from domain.enums import Environment
from service import SERVICE_ENV_PREFIX

from .application import ApplicationSettings
from .database import DatabaseSettings
from .http import HTTPSettings
from .logfire import LogfireSettings


class Settings(BaseSettings):
    """Validated root configuration loaded from environment and a local file."""

    model_config = SettingsConfigDict(
        env_prefix=f"{SERVICE_ENV_PREFIX}_",
        env_nested_delimiter="__",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        frozen=True,
        hide_input_in_errors=True,
        validate_default=True,
    )

    root_operation: PokerlostOperation = Field(
        description="Required API operation ID published for GET /.",
    )
    openapi_operation: PokerlostOperation = Field(
        description="Required API operation ID and path for OpenAPI publication.",
    )
    application: ApplicationSettings = Field(default_factory=ApplicationSettings)
    database: DatabaseSettings
    http: HTTPSettings = Field(default_factory=HTTPSettings)
    logfire: LogfireSettings = Field(default_factory=LogfireSettings)

    @model_validator(mode="after")
    def validate_production_observability(self) -> Self:
        """Fail fast when production telemetry delivery is disabled."""
        if self.application.environment is Environment.PRODUCTION and not (
            self.logfire.enabled and self.logfire.send_to_logfire
        ):
            raise ValueError("Production requires remote Logfire delivery")
        return self
