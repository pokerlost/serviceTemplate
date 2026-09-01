"""Application runtime resource lifecycle."""

from __future__ import annotations

from collections.abc import AsyncIterator, Callable
from contextlib import AbstractAsyncContextManager, asynccontextmanager

from fastapi import FastAPI

from application.ports import PokerlostTokenVerifier
from configuration import Settings
from observability import instrument_database
from persistence.database import create_database_engine, create_session_factory
from service import SERVICE_NAME

from .resources import ApplicationResources

type ApplicationLifespan = Callable[
    [FastAPI],
    AbstractAsyncContextManager[None, bool | None],
]


def create_lifespan(
    settings: Settings,
    *,
    token_verifier: PokerlostTokenVerifier | None,
) -> ApplicationLifespan:
    """Create and dispose the service runtime resources."""

    @asynccontextmanager
    async def lifespan(application: FastAPI) -> AsyncIterator[None]:
        engine = create_database_engine(
            settings.database,
            application_name=SERVICE_NAME,
        )
        instrument_database(engine, settings)
        application.state.resources = ApplicationResources(
            engine=engine,
            session_factory=create_session_factory(engine),
            token_verifier=token_verifier,
        )
        application.state.settings = settings
        try:
            yield
        finally:
            del application.state.resources
            del application.state.settings
            await engine.dispose()

    return lifespan
