"""ORM-backed public response configuration."""

from __future__ import annotations

from pydantic import ConfigDict

from api.schemas.base import ResponseModel


class ORMResponse(ResponseModel):
    """Immutable public response populated from ORM attributes."""

    model_config = ConfigDict(from_attributes=True)
