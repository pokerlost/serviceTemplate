"""Request-scoped transactional SQLAlchemy session dependency."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession

from api.errors.database import DatabaseUnavailableError

from .resources import ApplicationResourcesDep


async def _open_database_session(
    resources: ApplicationResourcesDep,
) -> AsyncIterator[AsyncSession]:
    """Yield one transaction that commits before the response is sent."""
    transaction = resources.session_factory.begin()
    try:
        session = await transaction.__aenter__()
    except (OSError, OperationalError) as exception:
        raise DatabaseUnavailableError from exception

    try:
        yield session
    except OperationalError as exception:
        try:
            await transaction.__aexit__(
                type(exception),
                exception,
                exception.__traceback__,
            )
        except (OSError, OperationalError) as database_exception:
            raise DatabaseUnavailableError from database_exception
        raise DatabaseUnavailableError from exception
    except BaseException as exception:
        try:
            await transaction.__aexit__(
                type(exception),
                exception,
                exception.__traceback__,
            )
        except (OSError, OperationalError) as database_exception:
            raise DatabaseUnavailableError from database_exception
        raise
    else:
        try:
            await transaction.__aexit__(None, None, None)
        except (OSError, OperationalError) as exception:
            raise DatabaseUnavailableError from exception


type DatabaseSession = Annotated[
    AsyncSession,
    Depends(_open_database_session, scope="function"),
]
