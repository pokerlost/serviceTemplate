"""Request-scoped transactional SQLAlchemy session dependency."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .resources import ApplicationResourcesDep


async def _open_database_session(
    resources: ApplicationResourcesDep,
) -> AsyncIterator[AsyncSession]:
    """Yield one request-owned PostgreSQL transaction."""
    async with resources.session_factory.begin() as session:
        yield session


type DatabaseSession = Annotated[
    AsyncSession,
    Depends(_open_database_session, scope="function"),
]
