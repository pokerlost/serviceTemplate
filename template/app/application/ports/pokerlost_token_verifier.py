"""Transport-independent local Pokerlost token-verification port."""

from __future__ import annotations

from typing import Protocol

from pypokerlost.types import PokerlostAuthorizationContext


class PokerlostTokenVerifier(Protocol):
    """Verify one access token locally for an exact target audience."""

    async def verify(
        self,
        token: str,
        *,
        audience: str,
    ) -> PokerlostAuthorizationContext:
        """Return immutable verified claims or raise InvalidAccessTokenError."""
        ...
