"""Asynchronous application handler port."""

from __future__ import annotations

from typing import Protocol

from application.command import Command
from application.query import Query
from application.result import Result


class Handler[RequestT: Command | Query, ResultT: Result](Protocol):
    """Handle one typed application request and return its result."""

    async def __call__(
        self,
        request: RequestT,
        /,
    ) -> ResultT:
        """Execute the application use case."""
        ...
