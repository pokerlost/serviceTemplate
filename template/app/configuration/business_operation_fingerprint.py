"""Business-operation fingerprint key settings."""

from __future__ import annotations

from typing import Self

from pydantic import Field, SecretStr, model_validator

from .base import SettingsModel


class BusinessOperationFingerprintSettings(SettingsModel):
    """Optional generic key configuration activated by concrete services."""

    secret: SecretStr | None = Field(
        default=None,
        description="Dedicated HMAC secret required by active idempotent operations.",
        repr=False,
    )
    key_version: int = Field(
        default=1,
        ge=1,
        description="Positive version of the active fingerprint key.",
    )

    @model_validator(mode="after")
    def validate_secret_length(self) -> Self:
        """Reject configured secrets shorter than 32 UTF-8 bytes."""
        if self.secret is not None and len(self.secret.get_secret_value().encode("utf-8")) < 32:
            raise ValueError(
                "Business-operation fingerprint secret must contain at least 32 UTF-8 bytes"
            )
        return self

    def require_secret(self) -> SecretStr:
        """Return the configured secret or fail composition for an active service."""
        if self.secret is None:
            raise ValueError("Business-operation fingerprint secret is required")
        return self.secret
