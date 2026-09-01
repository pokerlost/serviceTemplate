"""Body-only Pokerlost request authorization dependency."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Annotated, cast

from fastapi import Depends, Request
from fastapi.security import SecurityScopes
from pydantic import ValidationError
from pypokerlost.types import (
    JSONValue,
    PokerlostAuthorization,
    PokerlostAuthorizationContext,
    PokerlostScope,
)

from application.errors import (
    AuthenticationRequiredError,
    InsufficientScopeError,
    InvalidAccessTokenError,
)
from application.ports import PokerlostTokenVerifier
from service import SERVICE_NAME

from .resources import ApplicationResourcesDep


def _resolve_pokerlost_token_verifier(
    resources: ApplicationResourcesDep,
) -> PokerlostTokenVerifier:
    verifier = resources.token_verifier
    if verifier is None:
        raise RuntimeError("Pokerlost token verifier is not configured")
    return verifier


type PokerlostTokenVerifierDep = Annotated[
    PokerlostTokenVerifier,
    Depends(_resolve_pokerlost_token_verifier),
]


async def _read_authorization(request: Request) -> PokerlostAuthorization:
    """Validate only the authorization object from Starlette's cached JSON value."""
    try:
        body = cast(JSONValue, await request.json())
    except UnicodeDecodeError, ValueError:
        raise AuthenticationRequiredError from None
    if not isinstance(body, Mapping):
        raise AuthenticationRequiredError
    try:
        return PokerlostAuthorization.model_validate(body.get("authorization"))
    except ValidationError:
        raise AuthenticationRequiredError from None


async def authorize_pokerlost_request(
    request: Request,
    security_scopes: SecurityScopes,
    verifier: PokerlostTokenVerifierDep,
) -> PokerlostAuthorizationContext:
    """Verify body authentication, audience, and every exact required scope."""
    authorization = await _read_authorization(request)
    try:
        context = await verifier.verify(
            authorization.access_token,
            audience=SERVICE_NAME,
        )
    except InvalidAccessTokenError:
        raise
    if context.audience != SERVICE_NAME:
        raise InvalidAccessTokenError

    required_scopes = tuple(PokerlostScope(scope) for scope in security_scopes.scopes)
    granted_scopes = frozenset(context.scopes)
    if any(scope not in granted_scopes for scope in required_scopes):
        raise InsufficientScopeError
    return context
