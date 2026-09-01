# serviceTemplate ↔ pypokerlost compatibility

This is the canonical maintainer contract and verification procedure for the generated Pokerlost
server foundation.

## Authoritative SDK revision

```text
remote:               git@github.com:pokerlost/pypokerlost.git
distribution version: 0.2.0
current dependency:   a10cc8872c5de7e0065b3551e96d23fa2e99958f
foundation pin:       a10cc8872c5de7e0065b3551e96d23fa2e99958f
Python:               >=3.14
```

Replace the revision in this document, `template/pyproject.toml.jinja`, and
`scripts/check_rendered_template.py` only with the exact full SDK SHA confirmed on
`origin/main`. Lock generated services to that same revision. Never use a sibling path, local file
source, embedded credential, unverified index, or floating branch.

## Public compatibility boundary

The generated foundation relies on these flat SDK imports:

```python
from pypokerlost import PokerlostClient, PokerlostMethod, PokerlostRequestOptions
from pypokerlost.middleware import (
    PokerlostAuthorizationMiddleware,
    PokerlostMiddleware,
    PokerlostRetryMiddleware,
    PokerlostRetryPolicy,
    PokerlostTokenStore,
)
from pypokerlost.types import (
    PokerlostAccessTokenClaims,
    PokerlostAuthorization,
    PokerlostAuthorizationContext,
    PokerlostAuthorizedRequest,
    PokerlostClientCredentials,
    PokerlostOperation,
    PokerlostRequest,
    PokerlostResponse,
    PokerlostScope,
    PokerlostToken,
    PokerlostTokenState,
)
```

Generated operation imports are flat under `pypokerlost.methods`; generated wire/value types are
flat under `pypokerlost.types`. No service directories or contracts compatibility package are part
of the boundary.

## Operation protocol

Pokerlost APIs use a private JSON protocol over HTTPS. It is not standard OAuth2 and is not bearer
wire-compatible.

Every generated business method is:

```text
HTTP method: POST
path:        /<operationId>
operation:   ^[a-z][A-Za-z0-9]*$
request:     application/json
response:    PokerlostResponse[Result]
```

`GET /`, `GET /getOpenApi`, and existing health endpoints are public bodyless infrastructure
exceptions and are skipped by method generation where the generator already treats them as
system routes.

Public and token operations accept:

```json
{
  "payload": {}
}
```

Protected operations accept:

```json
{
  "authorization": {
    "access_token": "secret-value"
  },
  "payload": {}
}
```

There is no public generic transport-metadata option. Project code supplies only the JSON value to
the HTTP library.

## Token operations

`getToken` and `refreshToken` are ordinary public generated calls. Service credentials and refresh
credentials are serialized inside their respective JSON payloads. Neither operation requires an
access token.

`PokerlostToken` contains access token, optional refresh token, positive expiry seconds, exact
immutable scopes, and audience. It contains no token-type or transport representation and performs
no network or storage work. Secret-bearing fields are repr-hidden and validation-input-hidden.

Future authService stages may add separate typed grant operations. The template and generator do
not collapse them into a loose string-driven endpoint.

## Response contract

`PokerlostResponse[ResultT]` has exactly five fields:

```text
ok
result
error
error_message
retry_after
```

For success, result may be null and all failure metadata is null. For failure, result is null,
`error` is a stable code, `error_message` is optional sanitized text, and `retry_after` is optional
finite non-negative seconds. Invalid combinations are rejected through validation, never runtime
assertions.

The client decodes this envelope for both 2xx and non-2xx responses. A valid failed envelope raises
the canonical typed API error; malformed JSON/envelope/result raises a protocol error. Exceptions
never retain raw bodies, authentication material, or client credentials.

## Body authorization and scopes

`PokerlostScope` accepts at least two lowerCamelCase segments separated by dots:

```text
^[a-z][A-Za-z0-9]*(\.[a-z][A-Za-z0-9]*)+$
```

Operation IDs and scopes are independent. A generated method declares an exact immutable
`required_scopes` tuple; an empty tuple means public at transport level.

The server uses `PokerlostAuthorizedRequest[Payload]` and an ordinary FastAPI
`Security(authorize_pokerlost_request, scopes=[...])` dependency. OpenAPI represents the body
authorization schema but cannot encode exact body-token scopes. Compatibility therefore compares
the route dependency metadata with the generated method tuple for every implemented operation.

The template-owned `PokerlostTokenVerifier` port verifies locally and returns
`PokerlostAuthorizationContext`. It has no FastAPI, SQLAlchemy, or concrete JWT dependency. The
template does not provide a production verifier or call authService per inbound request.

## Middleware and retry

The canonical protected client flow is:

```text
PokerlostRetryMiddleware
→ PokerlostAuthorizationMiddleware
→ transport
```

Authorization middleware uses method `required_scopes`, audience, client credentials, a dedicated
auth-target client without authorization middleware, and a caller-supplied `PokerlostTokenStore`.
It reuses a token only beyond refresh skew, performs single-flight refresh/acquisition per audience
and exact scope set, and injects only `authorization.access_token` into an immutable authorized
request. Public methods bypass token lifecycle completely.

Retry is disabled unless the call supplies:

```python
options = PokerlostRequestOptions(
    retry_policy=PokerlostRetryPolicy(),
)
```

The immutable policy has three attempts including the first, initial delay `0.2`, maximum delay
`2.0`, multiplier `2.0`, full jitter, and a `5.0` second logical budget. Retryable statuses are
`408`, `425`, `429`, `500`, `502`, `503`, and `504`; canonical connection and timeout failures are
also retryable. Server delay comes only from body `retry_after` and must fit the remaining budget.
Exhaustion re-raises the last canonical error.

Authentication failure invalidates matching token state but never replays the current call.
Insufficient scope does not refresh or retry. Cancellation and protocol errors propagate.

Transport retry is distinct from business idempotency. Mutation replay requires the same business
operation ID, semantic payload, operation, and target. Middleware does not generate those values or
own workflow persistence.

## OpenAPI and generation

FastAPI emits the standard OpenAPI 3.1 document without project extensions, service identity, or a
misleading header security scheme. The generator validates all source documents together before
writing:

```text
single lowerCamelCase operation ID
path equals /<operationId>
POST business operation
application/json request
canonical request envelope
canonical response envelope
global operation and schema uniqueness
flat method/type output
```

The generator never derives exact scopes from prose. Implemented handwritten method metadata or an
explicit checked input outside OpenAPI remains the scope source. Manual future-facing SDK stubs are
not generator-owned unless the manifest says otherwise.

## Mandatory compatibility probe

Use Copier 9.17.2, a disposable generated service, and the authoritative SDK environment:

1. Render `exampleService`, resolve the pinned SDK dependency, and run generated checks.
2. Confirm `GET /` is `getRoot` and `GET /getOpenApi` is `getOpenApi`, both bodyless and public.
3. Confirm no OpenAPI extension or security scheme is added by the template.
4. Add a disposable public `POST /echoMessage` route using `PokerlostRequest` and
   `PokerlostResponse`; generate and call its flat SDK method.
5. Add a disposable protected `POST /getMe` route using `PokerlostAuthorizedRequest` and
   `Security(..., scopes=[Scope.READ_SELF])`.
6. Supply a disposable local verifier and probe missing authorization, malformed authorization,
   invalid token, wrong audience, missing scope, and exact-scope success.
7. Confirm the published protected request schema requires `authorization.access_token`, while the
   public schema has no authorization field.
8. Compare route scopes with the generated method `required_scopes` tuple.
9. Probe public middleware bypass, cached-token use, body token acquisition, body refresh,
   single-flight acquisition, `401` invalidation without replay, and `403` propagation.
10. Probe retry disabled, connection/timeout retry, retryable/non-retryable status handling, body
    `retry_after`, budget enforcement, cancellation, and final-error preservation.
11. Confirm no request/response body, token, password, client secret, or private key appears in
    reprs, validation errors, logs, spans, or SDK exceptions.
12. Run negatives for dotted, snake_case, hyphenated, and uppercase operation IDs; invalid scope
    segments; path mismatch; unsupported methods/media; and global collisions.
13. Generate from the final auth/accounts OpenAPI sources until a second run produces no diff.
14. Remove every disposable route, verifier, generated file, captured document, bytecode file, and
    process.

## Copier regression

Every compatibility change requires a fresh render and an update from the exact prior template
commit. Confirm service-owned `SERVICE.md`, concrete handlers, migrations, and scope values remain
unchanged; obsolete unchanged template-owned files disappear; the new flat routers and body-auth
foundation appear; and `.copier-answers.yml` remains valid.

The pristine settings, resources, environment example, and Helm chart contain no outbound target,
credential, token store, retry tuning, or fake verifier. Production deployment remains behind
mandatory HTTPS/TLS termination.
