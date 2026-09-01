"""Runtime resources owned by the application lifespan."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from application.ports import PokerlostTokenVerifier


@dataclass(frozen=True, slots=True)
class ApplicationResources:
    """Reusable process resources shared by request dependencies."""

    engine: AsyncEngine
    session_factory: async_sessionmaker[AsyncSession]
    token_verifier: PokerlostTokenVerifier | None
