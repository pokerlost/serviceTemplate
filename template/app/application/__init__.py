"""Application contract facade."""

from __future__ import annotations

from .command import Command
from .query import Query
from .result import Result

__all__ = ("Command", "Query", "Result")
