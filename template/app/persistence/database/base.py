"""Typed SQLAlchemy declarative bases and shared naming conventions."""

from __future__ import annotations

from typing import Final

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.util import immutabledict

from .mixins import UUIDPrimaryKeyMixin

NAMING_CONVENTION: Final[immutabledict[str, str]] = immutabledict(
    {
        "ix": "ix_%(table_name)s_%(column_0_name)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(column_0_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    },
)


class Base(DeclarativeBase):
    """Declarative base for all SQLAlchemy ORM models."""

    metadata = MetaData(naming_convention=NAMING_CONVENTION)


class UUIDModel(UUIDPrimaryKeyMixin, Base):
    """Abstract base for entities with a standard UUID primary key."""

    __abstract__ = True
