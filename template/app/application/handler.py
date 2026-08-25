"""Asynchronous application handler contract."""

from __future__ import annotations

from abc import ABC, abstractmethod

from .command import Command
from .query import Query
from .result import Result


class Handler[InputT: Command | Query, ResultT: Result](ABC):
    """Execute one typed command or query and return an application result."""

    @abstractmethod
    async def execute(self, input_: InputT, /) -> ResultT:
        """Execute the application operation."""
        raise NotImplementedError
