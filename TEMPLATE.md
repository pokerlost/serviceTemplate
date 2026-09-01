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

## Private JSON protocol

Pokerlost services use a private body-only JSON operation protocol over HTTPS. The wire contract is
not standard OAuth2 and does not imitate a header-oriented security scheme.

The only public infrastructure exceptions are:

```text
GET /
GET /getOpenApi
existing liveness/readiness GET probes
```

They accept neither a business body nor authentication. Every business/API operation follows:

```text
POST /<operationId>
request  = PokerlostRequest[Payload] or PokerlostAuthorizedRequest[Payload]
response = PokerlostResponse[Result]
```

Operation IDs match `^[a-z][A-Za-z0-9]*$`, start with a verb, and use one lowerCamelCase segment.
Business paths equal `"/" + operationId`. Inputs do not use path, query, cookie, form, generic
transport metadata, or GET bodies. Project code sends ordinary JSON and does not construct framing
metadata manually.

Public requests contain only `payload`. Protected requests contain `authorization.access_token`
and `payload`; a token has no type prefix. Client credentials are fields of the `getToken` payload,
and refresh credentials are fields of the `refreshToken` payload.

## Response and error contract

`pypokerlost.types.PokerlostResponse[ResultT]` is the only API envelope. Its fields are:

```text
ok
result
error
error_message
retry_after
```

Success has no error metadata or retry delay. Failure has a stable error code, null result, an
optional sanitized message, and an optional finite non-negative delay in seconds. Server retry
guidance exists only in this JSON field. Central handlers create validated envelopes and never
echo submitted values, raw bodies, traces, SQL details, or secrets.

Local `RequestModel` and `ResponseModel` remain bases for operation payload/result schemas. They
are not alternate request or response envelopes. Routes translate persistence values into public
results explicitly instead of relying on an ORM-backed response base.

## Body authorization foundation

The template provides a reusable seam without implementing production token verification:

```text
app/api/scopes.py
app/api/dependencies/authorization.py
app/application/ports/pokerlost_token_verifier.py
```

The pristine `Scope` catalog is empty. Concrete services add exact dot-separated lowerCamelCase
values, validated through `PokerlostScope`. Wildcards are invalid.

`PokerlostTokenVerifier` is a transport-independent local verifier port. `create_app()` accepts an
optional concrete verifier and stores it in `ApplicationResources`; protected composition without
one fails closed. The template does not create a fake verifier, JWT implementation, target client,
credentials, or token store.

`authorize_pokerlost_request` reads Starlette's cached JSON value, validates only the authorization
object, verifies the token locally for the service audience, compares the returned audience, and
requires every exact `SecurityScopes` value. It never uses a role as authorization and never calls
authService per request.

Concrete routes compose authorization through ordinary FastAPI `Security`:

```python
authorization: Annotated[
    PokerlostAuthorizationContext,
    Security(
        authorize_pokerlost_request,
        scopes=[Scope.READ_SELF],
    ),
]
```

Public routes omit that dependency and use `PokerlostRequest`. Protected routes use
`PokerlostAuthorizedRequest`.

## OpenAPI and routers

FastAPI produces the unmodified OpenAPI 3.1 document. The template adds no project extension,
service identity, Python import metadata, or custom authorization metadata. It does not publish a
misleading OAuth2, API-key, or other header-oriented security scheme.

Body authentication appears honestly in the protected request schema. OpenAPI cannot express the
exact scopes required by a body token, so maintainers compare two canonical sources: the route
`Security(..., scopes=[...])` declaration and the generated SDK method's `required_scopes` tuple.

Built-in schema and documentation URLs remain disabled. `GET /getOpenApi` returns the ordinary
document inside `PokerlostResponse`.

Routers are flat modules such as `app/api/routers/root.py`, `app/api/routers/openapi.py`, and
`app/api/routers/get_me.py`. Each module owns one factory and one primary decorated endpoint. There
are no one-directory-per-router packages, imperative route registration, route operation
constants, or post-hoc mutation.

## Outbound SDK boundary

The SDK owns HTTP transport, generated methods, request envelopes, response decoding, canonical
errors, authorization middleware, retry middleware, and token lifecycle coordination. A concrete
consumer supplies target configuration, client credentials, a token store implementation, and a
dedicated auth-target `PokerlostClient` without authorization middleware.

Protected client composition is:

```text
PokerlostRetryMiddleware
→ PokerlostAuthorizationMiddleware
→ transport
```

Retry is explicit per call through
`PokerlostRequestOptions(retry_policy=PokerlostRetryPolicy())`. The shared immutable policy uses at
most three attempts including the first, full jitter, a five-second logical budget, and body
`retry_after`. Authentication failures invalidate token state for a later independent call but do
not replay the current call. Insufficient scope never refreshes or retries.

Transport retry does not create business idempotency. A replayable mutation must reuse its own
business operation ID, semantic payload, operation, and target. No PostgreSQL transaction remains
open during token acquisition, remote calls, retry sleep, or later attempts.

## Privacy and observability

Pydantic request/settings models hide validation input where secrets may appear. Secret fields are
repr-hidden. FastAPI instrumentation disables header and body capture; Logfire argument inspection
is disabled and focused scrubbing covers authentication and credential terms. Central validation
and unexpected-error responses are sanitized.

Request IDs are generated only by the server and stored in request state/telemetry. The template
does not read caller correlation metadata or return request identifiers as a public transport
contract.

## Generated architecture and deployment

The source tree separates `api`, `application`, `domain`, `configuration`, `observability`,
`persistence`, and `cli`. The application foundation includes immutable `Command`, `Query`, and
`Result` values plus the structural asynchronous `Handler` port. Persistence provides reusable
SQLAlchemy metadata, narrow repository execution, and one request-owned transaction, without a
concrete model, read-projection framework, or migration.

Production deployment requires HTTPS/TLS. The generated Helm service is an internal ClusterIP that
must remain behind trusted TLS termination; it is not a plaintext production edge. Secrets enter
through Kubernetes Secret references rather than chart values or ConfigMaps.

## Ownership and intentional omissions

Copier owns the reusable scaffold. Generated services own `SERVICE.md`, their domain, handlers,
persistence entities, migrations, scopes, concrete verifier, and implemented routes. Copier
updates must preserve those files and service meaning.

The pristine template intentionally contains no business operation, concrete entity, fake
migration, login flow, token grant, refresh persistence, JWKS implementation, production verifier,
outbound client, credential, token store, role policy, worker, gateway, or workflow framework.

The release history is in `CHANGELOG.md`; copy/update steps are in `CREATE_SERVICE.md`; the exact
SDK compatibility procedure is in `SDK_COMPATIBILITY.md`.
