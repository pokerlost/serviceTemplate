"""Logfire observability facade."""

from __future__ import annotations

from .configuration import configure_observability
from .fastapi import instrument_fastapi
from .sqlalchemy import instrument_database

__all__ = (
    "configure_observability",
    "instrument_database",
    "instrument_fastapi",
)
