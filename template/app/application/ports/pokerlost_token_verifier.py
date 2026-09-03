"""Transport-independent local Pokerlost token-verification port."""

from __future__ import annotations

from typing import Protocol

from pydantic import SecretStr
from pypokerlost.types import PokerlostAudience, PokerlostAuthorizationContext


class PokerlostTokenVerifier(Protocol):
    """Verify one access token locally for an exact target audience."""

    async def verify(
        self,
        token: SecretStr,
        *,
        audience: PokerlostAudience,
    ) -> PokerlostAuthorizationContext:
        """Return verified claims or raise an invalid/expired token application error."""
        ...
