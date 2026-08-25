"""Application output base."""

from __future__ import annotations

from domain.value_model import ValueModel


class Result(ValueModel):
    """Marker base for typed application output."""
