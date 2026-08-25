"""Application mutation input base."""

from __future__ import annotations

from domain.value_model import ValueModel

class Command(ValueModel):
    """Marker base for typed application mutation input."""
