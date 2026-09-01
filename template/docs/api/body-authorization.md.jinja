# Body authorization

Protected Pokerlost operations carry authentication only inside their JSON request body.

## Request shape

```json
{
  "authorization": {
    "access_token": "secret-value"
  },
  "payload": {}
}
```

The token has no type prefix and appears nowhere else in the HTTP request. Public requests contain
only `payload` and never receive authentication automatically.

## Local verifier seam

`app/application/ports/pokerlost_token_verifier.py` defines the framework-independent
`PokerlostTokenVerifier` port. The pristine service has no concrete verifier. A service supplies a
real local implementation to `create_app()` only when an implemented route requires protection;
otherwise protected composition fails closed.

`app/api/dependencies/authorization.py` reads Starlette's cached JSON value, validates only the
`authorization` field through `PokerlostAuthorization`, verifies for the service audience, compares
the returned audience, and checks every exact required scope. It never makes a remote authService
call and never uses a role as a bypass.

## Route composition

```python
from typing import Annotated

from fastapi import APIRouter, Security
from pypokerlost.types import (
    PokerlostAuthorizationContext,
    PokerlostAuthorizedRequest,
    PokerlostResponse,
)

from api.dependencies import authorize_pokerlost_request
from api.scopes import Scope


@router.post(
    path="/getMe",
    operation_id="getMe",
    response_model=PokerlostResponse[AccountResponse],
)
async def get_me(
    request: PokerlostAuthorizedRequest[GetMeRequest],
    authorization: Annotated[
        PokerlostAuthorizationContext,
        Security(
            authorize_pokerlost_request,
            scopes=[Scope.READ_SELF],
        ),
    ],
) -> PokerlostResponse[AccountResponse]: ...
```

The service-owned `Scope` catalog is a flat `StrEnum`; every member is validated through
`PokerlostScope`. Values use dot-separated lowerCamelCase segments and never wildcards.

Missing/malformed body authentication maps to `AUTHENTICATION_REQUIRED`, invalid token/audience to
`INVALID_ACCESS_TOKEN`, and missing exact scope to `INSUFFICIENT_SCOPE`.

## OpenAPI limitation

The protected request schema honestly shows `authorization.access_token`. OpenAPI cannot express
the exact scopes required by a body token, so reviewers compare the route's
`Security(..., scopes=[...])` declaration with the matching generated SDK method's
`required_scopes` tuple. No custom extension or misleading security scheme fills that gap.

## Privacy

Token-bearing models hide representations and validation inputs. Validation responses, logs,
spans, and exceptions never include the raw body or token. FastAPI instrumentation keeps body
capture disabled.
