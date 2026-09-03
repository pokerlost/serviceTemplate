"""OAuth2 bearer authorization for protected Pokerlost operations."""

from __future__ import annotations

from typing import Annotated

from fastapi import Security
from fastapi.openapi.models import OAuthFlowClientCredentials, OAuthFlows
from fastapi.security import OAuth2, SecurityScopes
from fastapi.security.utils import get_authorization_scheme_param
from pydantic import SecretStr
from pypokerlost.types import (
    PokerlostAudience,
    PokerlostAuthorizationContext,
)

from application.errors import (
    AuthenticationRequiredError,
    InsufficientScopeError,
    InvalidAccessTokenError,
)
from application.ports import PokerlostTokenVerifier
from domain.enums import Scopes, scope_descriptions
from service import SERVICE_NAME

from .resources import ApplicationResourcesDep


def _resolve_pokerlost_token_verifier(resources: ApplicationResourcesDep) -> PokerlostTokenVerifier:
    verifier = resources.token_verifier
    if verifier is None:
        raise RuntimeError("Pokerlost token verifier is not configured")
    return verifier


_SERVICE_AUDIENCE = PokerlostAudience(SERVICE_NAME)
_pokerlost_oauth2_scheme = OAuth2(
    flows=OAuthFlows(
        clientCredentials=OAuthFlowClientCredentials(
            tokenUrl="/getToken",
            scopes=scope_descriptions(),
        ),
    ),
    scheme_name="PokerlostOAuth2",
    description="Pokerlost service access token with exact capability scopes.",
    auto_error=False,
)

type PokerlostAuthorizationHeader = Annotated[
    str | None,
    Security(_pokerlost_oauth2_scheme),
]


def _parse_route_scopes(security_scopes: SecurityScopes) -> tuple[Scopes, ...]:
    """Validate the protected-route scope declaration before token verification."""
    if not security_scopes.scopes:
        raise RuntimeError("Protected Pokerlost operations require at least one exact scope")
    try:
        route_scopes = tuple(Scopes(scope) for scope in security_scopes.scopes)
    except ValueError:
        raise RuntimeError("Protected Pokerlost operation declares an unknown scope") from None
    if len(frozenset(route_scopes)) != len(route_scopes):
        raise RuntimeError("Protected Pokerlost operation declares duplicate scopes")
    return route_scopes


def _read_bearer_token(authorization_header: str | None) -> SecretStr:
    """Extract one non-empty bearer credential without exposing it in errors."""
    if authorization_header is None:
        raise AuthenticationRequiredError
    scheme, token = get_authorization_scheme_param(authorization_header)
    if (
        scheme.casefold() != "bearer"
        or not token
        or any(character.isspace() for character in token)
    ):
        raise AuthenticationRequiredError
    return SecretStr(token)


async def authorize_pokerlost_request(
    security_scopes: SecurityScopes,
    authorization_header: PokerlostAuthorizationHeader,
    resources: ApplicationResourcesDep,
) -> PokerlostAuthorizationContext:
    """Verify bearer authentication, audience, and every exact required scope."""
    route_scopes = _parse_route_scopes(security_scopes)
    token = _read_bearer_token(authorization_header)
    verifier = _resolve_pokerlost_token_verifier(resources)
    context = await verifier.verify(token, audience=_SERVICE_AUDIENCE)
    if context.audience != _SERVICE_AUDIENCE:
        raise InvalidAccessTokenError

    granted_scope_values = frozenset(scope.value for scope in context.scopes)
    if any(scope.value not in granted_scope_values for scope in route_scopes):
        raise InsufficientScopeError
    return context
