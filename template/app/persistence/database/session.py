"""Async SQLAlchemy engine and session construction primitives."""

from __future__ import annotations

from sqlalchemy import event
from sqlalchemy.engine import Dialect
from sqlalchemy.engine.interfaces import DBAPIConnection
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import ConnectionPoolEntry

from configuration.database import DatabaseSettings


def _connect_with_availability_translation(
    dialect: Dialect,
    _connection_record: ConnectionPoolEntry,
    connection_args: tuple[object, ...],
    connection_parameters: dict[str, object],
) -> DBAPIConnection:
    """Normalize an asyncpg connection refusal to SQLAlchemy's availability category."""
    try:
        return dialect.connect(*connection_args, **connection_parameters)
    except ConnectionRefusedError as exception:
        raise OperationalError(
            statement=None,
            params=None,
            orig=exception,
            hide_parameters=True,
            connection_invalidated=True,
        ) from exception


def create_database_engine(
    settings: DatabaseSettings,
    *,
    application_name: str,
) -> AsyncEngine:
    """Create the process-level async PostgreSQL engine."""
    engine = create_async_engine(
        settings.url.get_secret_value(),
        pool_pre_ping=True,
        pool_size=settings.pool_size,
        max_overflow=settings.max_overflow,
        pool_timeout=settings.pool_timeout_seconds,
        connect_args={
            "command_timeout": settings.command_timeout_seconds,
            "server_settings": {"application_name": application_name},
        },
        hide_parameters=True,
    )
    event.listen(
        engine.sync_engine,
        "do_connect",
        _connect_with_availability_translation,
    )
    return engine


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Create request-scoped async sessions for explicit transaction ownership."""
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        autoflush=False,
        expire_on_commit=False,
    )
