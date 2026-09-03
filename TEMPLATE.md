# Pokerlost Service Template

This document defines the reusable foundation rendered by `serviceTemplate` and the boundaries a
pristine generated service preserves.

## Generation contract

Copier 9.17.2 asks only for `service_name` and derives `service_slug`, `service_env_prefix`, and
`database_name`. Generated services require Python 3.14 or newer and include FastAPI, PostgreSQL,
SQLAlchemy, Alembic, Logfire, Docker, Helm, uv, Ruff, mypy, and pre-commit.

Every generated service pins the private `pypokerlost` Git source to one full commit already
published on `origin/main`. Builds may forward an SSH agent and trusted GitHub host keys only while
the builder resolves dependencies. Repository credentials never enter the runtime image or chart.

## JSON and HTTP protocol

Every business/API operation uses:

```text
POST /<operationId>
Content-Type: application/json
request  = PokerlostRequest[Payload]
response = PokerlostResponse[Result]
```

Operation IDs match `^[a-z][A-Za-z0-9]*$`, start with a verb, and use one globally unique
lowerCamelCase segment. Business paths equal `"/" + operationId`.

The infrastructure exceptions are `GET /`, `GET /getOpenApi`, and existing health probes. They
accept neither a business body nor authentication. Business inputs do not use path, query, cookie,
form, generic transport metadata, or GET bodies.

Protected operations receive an access token only through:

```text
Authorization: Bearer <access-token>
```

The request body never contains authorization, access tokens, generic headers, request options, or
middleware state. Client credentials remain typed fields of `getToken`; refresh credentials remain
typed fields of `refreshToken`.

## Response and error contract

`pypokerlost.types.PokerlostResponse[ResultT]` is the only API envelope. Its fields are `ok`,
`result`, `error`, `error_message`, and `retry_after`. Success has no error metadata or retry delay.
Failure has a stable code, null result, an optional sanitized message, and an optional finite
non-negative delay in seconds.

Normal endpoints declare the canonical `PokerlostResponse[ResultT]` as their FastAPI
`response_model`, return plain mappings/data, and let FastAPI validate and serialize successes.
Application handlers return focused application results and do not know about FastAPI or response
envelopes. Central handlers alone construct handled failure envelopes, including authentication and
authorization errors. They never emit FastAPI `detail`, echo submitted values or raw bodies, or
retain secrets. `error_response()` is the only manual envelope serialization helper and carries
`retry_after` solely in the body.

The shared platform authentication codes are:

```text
POKERLOST_AUTHENTICATION_REQUIRED
POKERLOST_ACCESS_TOKEN_INVALID
POKERLOST_ACCESS_TOKEN_EXPIRED
POKERLOST_INSUFFICIENT_SCOPE
```

## Standard OAuth2 authorization

The generated foundation provides:

```text
app/domain/enums/scopes.py
app/api/dependencies/authorization.py
app/application/ports/pokerlost_token_verifier.py
```

`Scopes` is the service-owned `StrEnum`. Values contain dotted lowerCamelCase capability segments;
underscores, hyphens, wildcards, and duplicate values are invalid. The focused
`scope_descriptions()` function is the only OpenAPI description mapping.

The authorization dependency owns one FastAPI `OAuth2` scheme named `PokerlostOAuth2`, with a
client-credentials flow, `/getToken`, the complete local scope catalog, and `auto_error=False`.
FastAPI emits its ordinary OpenAPI `securitySchemes` component and exact per-operation `security`
requirement without extensions or mutation.

A public route omits the dependency. A protected route uses a non-empty exact list:

```python
authorization: Annotated[
    PokerlostAuthorizationContext,
    Security(
        authorize_pokerlost_request,
        scopes=[Scopes.ACCOUNTS_SELF_GET_ME],
    ),
]
```

The dependency rejects missing/malformed headers, invokes the local verifier with a `SecretStr`
and exact `SERVICE_NAME` audience, distinguishes invalid and expired tokens, compares audience, and
checks `required scopes <= verified scopes`. It never checks roles or calls authService per request.

Expired-token rejection occurs before the endpoint handler and business effects. Calling the
dependency with no scopes is a programming error, not authenticated access without scopes.

## OpenAPI and generation

FastAPI produces the unmodified OpenAPI 3.1 document; `GET /getOpenApi` returns that document
directly. Built-in schema and documentation URLs remain disabled.

The SDK generator validates all service documents together. `PokerlostScopes` is the explicit
SDK-owned shared catalog. Standard OAuth2 metadata supplies each implemented protected operation's
exact scopes, and the generator requires every extracted value to exist in that catalog. A document
with no protected operation may omit `components.securitySchemes`; its public methods use
`__scopes__ = None`. Once an operation is protected, the supported standard OAuth2 scheme and a
non-empty exact scope list are mandatory. Empty scope requirements, unknown schemes/scopes, mixed
alternatives, or global operation collisions fail generation.

Routers remain flat modules with one module-level `router = APIRouter(...)` and module-level
decorated endpoints. Static router factories and nested endpoints are forbidden. Generated and
handwritten SDK methods and types remain flat; SDK-owned enums form an explicit flat catalog.

## Outbound SDK boundary

The SDK owns HTTP transport, generated contracts, canonical response decoding/errors, retry,
bearer injection, and the protocol boundary for one reactive refresh. It does not store client
credentials, call `GetToken` automatically, persist state, run background refresh, or own service
scope policy.

A consuming service explicitly acquires the initial token, then persists encrypted token state
with an absolute timezone-aware UTC expiration and positive version. Its injected token store uses
compare-and-swap semantics. Its injected refresher owns distributed lease/CAS coordination and
invokes `RefreshToken` through a dedicated auth client without holding a PostgreSQL transaction
during network I/O.

For `method.__scopes__ is None`, middleware bypasses token state and sends no Authorization header.
For a non-empty tuple, it loads the exact client/audience/scope key. Missing metadata, an empty
tuple, or missing state fails locally.

Local expiration metadata does not trigger refresh by itself. Exactly
`POKERLOST_ACCESS_TOKEN_EXPIRED` may trigger one refresh and one identical replay. Invalid token,
insufficient scope, or a second expiration never triggers another refresh.

Retry remains explicit through `PokerlostRequestOptions(retry_policy=PokerlostRetryPolicy())`.
Body `retry_after` is the only server delay input. Transport retry is not business idempotency; a
replayable mutation must preserve its business operation ID and semantic payload.

## Privacy, persistence, and deployment

Secret fields are repr-hidden and Pydantic input hiding is enabled. FastAPI instrumentation captures
neither headers nor bodies. Central errors and logs retain no credentials, tokens, Authorization
headers, or raw payloads.

PostgreSQL remains the source of truth for generated-service persistence. One request owns one
transaction. No transaction spans token acquisition, refresh, remote calls, or retry sleep.

Production deployment requires HTTPS/TLS. The generated Helm service is an internal ClusterIP
behind trusted TLS termination. Secrets enter through Kubernetes Secret references, not chart
values or ConfigMaps.

## Ownership and intentional omissions

Copier owns the reusable scaffold. Generated services own `SERVICE.md`, domain behavior, handlers,
persistence entities, migrations, concrete domain enums and scopes, verifier, token
persistence/refresher adapters, and implemented routes. Copier updates preserve service meaning
and service-owned files.

The pristine template intentionally contains no business operation, concrete entity, fake
migration, production verifier, outbound client, credential, token store, crypto primitive, role
policy, worker, gateway, or workflow framework.

The release history is in `CHANGELOG.md`; copy/update steps are in `CREATE_SERVICE.md`; the exact
SDK compatibility procedure is in `SDK_COMPATIBILITY.md`.
