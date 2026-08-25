"""Privacy-safe PostgreSQL SQLAlchemy Logfire instrumentation."""

from __future__ import annotations

import logfire
from sqlalchemy.ext.asyncio import AsyncEngine

from configuration import Settings


def instrument_database(engine: AsyncEngine, settings: Settings) -> None:
    """Instrument the concrete async SQLAlchemy engine once."""
    if not settings.logfire.enabled:
        return

    logfire.instrument_sqlalchemy(engine=engine)
