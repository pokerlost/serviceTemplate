"""Application contract facade."""

from __future__ import annotations

from .command import Command
from .handler import Handler
from .query import Query
from .result import Result

__all__ = ("Command", "Handler", "Query", "Result")
