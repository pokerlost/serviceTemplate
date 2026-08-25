"""Application read input base."""

from __future__ import annotations

from domain.value_model import ValueModel


class Query(ValueModel):
    """Marker base for typed application read input."""
