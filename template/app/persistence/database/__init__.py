"""Public SQLAlchemy database foundation facade."""

from __future__ import annotations

from .base import Base, UUIDModel
from .session import create_database_engine, create_session_factory

# Keep this import after the base exports so future models may import UUIDModel from this facade.
from . import models as models  # isort: skip

__all__ = (
    "Base",
    "UUIDModel",
    "create_database_engine",
    "create_session_factory",
    "models",
)
