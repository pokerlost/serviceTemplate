"""Public request model configuration."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class RequestModel(BaseModel):
    """Closed base for application-owned API request bodies."""

    model_config = ConfigDict(
        allow_inf_nan=False,
        extra="forbid",
        hide_input_in_errors=True,
        validate_default=True,
    )
