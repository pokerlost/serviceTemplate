# Header authorization

Protected Pokerlost operations accept one access token through the standard HTTP Authorization
header and verify it locally before entering the endpoint handler.

## Request shape

```text
Authorization: Bearer <access-token>
Content-Type: application/json
```

The JSON body remains the pure `PokerlostRequest[Payload]` envelope:

```json
{
  "payload": {}
}
```

The body contains no access token, authorization object, generic headers, request options, or
middleware state. Public operations use the same body envelope but send no Authorization header.

## Standard OAuth2 metadata

`app/api/dependencies/authorization.py` owns one FastAPI `OAuth2` scheme named
`PokerlostOAuth2`. It uses a client-credentials flow, `/getToken` as its token URL, the complete
`app/domain/enums/scopes.py` description catalog, and `auto_error=False`.

FastAPI therefore publishes the standard OpenAPI scope catalog under
`components.securitySchemes` and the exact non-empty route scope list under the operation's
`security` requirement. The service adds no `openapi_extra`, vendor extension, scope map, or
post-processing mutation.

When no production route uses the dependency, FastAPI may omit the unused security scheme. That is
a valid public-only contract and does not require a fake route, schema injection, or empty security
requirement.

A public operation omits `Security(authorize_pokerlost_request, ...)` entirely and has no OpenAPI
security requirement. Calling the authorization dependency with an empty scope list is a
programming error; it never means public access.

## Local verifier seam

`app/application/ports/pokerlost_token_verifier.py` defines the framework-independent
`PokerlostTokenVerifier` port. The pristine service has no concrete verifier. A service supplies a
real local implementation to `create_app()` only when an implemented route requires protection;
otherwise protected composition fails closed.

The dependency parses the OAuth2 value as a non-empty bearer header, verifies the secret token for
the exact `SERVICE_NAME` audience, compares the returned audience, and requires every exact route
scope. It never makes a remote authService call and never uses a role.

## Route composition

```python
from typing import Annotated

from fastapi import APIRouter, Security
from pypokerlost.types import (
    PokerlostAuthorizationContext,
    PokerlostRequest,
    PokerlostResponse,
)

from api.dependencies import GetMeHandlerDep, authorize_pokerlost_request
from domain.enums import Scopes

router = APIRouter(tags=["accounts"])


@router.post(
    path="/getMe",
    operation_id="getMe",
    response_model=PokerlostResponse[GetMeResponse],
)
async def get_me(
    request: PokerlostRequest[GetMeRequest],
    handler: GetMeHandlerDep,
    authorization: Annotated[
        PokerlostAuthorizationContext,
        Security(
            authorize_pokerlost_request,
            scopes=[Scopes.ACCOUNTS_SELF_GET_ME],
        ),
    ],
) -> dict[str, object]:
    result = await handler(request.payload)
    return {"ok": True, "result": result}
```

The service-owned `Scopes` catalog is a domain `StrEnum`. Values use dotted lowerCamelCase
segments, never underscores, hyphens, or wildcards. `scope_descriptions()` is the single
description source for OpenAPI.

## Failures and replay safety

Missing or malformed bearer authentication maps to `POKERLOST_AUTHENTICATION_REQUIRED`, invalid
token or audience to `POKERLOST_ACCESS_TOKEN_INVALID`, expired token to
`POKERLOST_ACCESS_TOKEN_EXPIRED`, and missing exact scope to `POKERLOST_INSUFFICIENT_SCOPE`.
Central handlers serialize every failure as `PokerlostResponse` without a FastAPI `detail` body.

Expired-token rejection occurs in this dependency before the endpoint handler and before business
effects. That invariant permits the SDK authorization middleware to perform at most one reactive
refresh and replay. Invalid tokens and insufficient scope never trigger refresh.

## Privacy

The verifier receives a `SecretStr`. Validation responses, logs, spans, and exceptions never
include the raw header or token. FastAPI instrumentation keeps header and body capture disabled.
