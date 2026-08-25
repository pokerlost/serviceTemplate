"""Mandatory PostgreSQL connection and pool settings."""

from __future__ import annotations

from typing import Self

from pydantic import Field, SecretStr, model_validator
from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError

from .base import SettingsModel


class DatabaseSettings(SettingsModel):
    """Validated async PostgreSQL runtime configuration."""

    url: SecretStr = Field(
        description="Required SQLAlchemy postgresql+asyncpg connection URL.",
        repr=False,
    )
    pool_size: int = Field(default=10, ge=1, le=100)
    max_overflow: int = Field(default=10, ge=0, le=100)
    pool_timeout_seconds: float = Field(default=10.0, gt=0, le=120)
    command_timeout_seconds: float = Field(default=30.0, gt=0, le=300)

    @model_validator(mode="after")
    def validate_connection_url(self) -> Self:
        """Require a complete asyncpg PostgreSQL URL without exposing it."""
        try:
            parsed_url = make_url(self.url.get_secret_value())
        except ArgumentError:
            raise ValueError("Database URL must be a valid SQLAlchemy URL") from None

        if parsed_url.drivername != "postgresql+asyncpg":
            raise ValueError("Database URL driver must be postgresql+asyncpg")
        if not all(
            (
                parsed_url.username,
                parsed_url.password,
                parsed_url.host,
                parsed_url.database,
            )
        ):
            raise ValueError("Database URL must include username, password, host, and database")
        return self
