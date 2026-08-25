"""Async SQLAlchemy engine and session construction primitives."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from configuration.database import DatabaseSettings


def create_database_engine(
    settings: DatabaseSettings,
    *,
    application_name: str,
) -> AsyncEngine:
    """Create the process-level async PostgreSQL engine."""
    return create_async_engine(
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


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Create request-scoped async sessions for explicit transaction ownership."""
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        autoflush=False,
        expire_on_commit=False,
    )
