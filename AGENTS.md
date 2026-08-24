# PokerLost FastAPI Service Template — Repository Rules

> This file is the mandatory architectural source of truth for a PokerLost FastAPI service.
> Complete the Service Profile before implementing service-specific behavior.
> The pristine TEMPLATE repository contains infrastructure only; it is not an implementation of
> any concrete service.

---

# Service Profile — Must Be Completed

```text
SERVICE_NAME: <canonical human-facing name, e.g. accountService>
SERVICE_SLUG: <lowercase DNS/Kubernetes name, e.g. accountservice>
SERVICE_PURPOSE: <one paragraph>
SERVICE_ROLE: <AUTH | FINANCIAL | CRYPTO | POKER | GENERAL>
DATA_OWNERSHIP: <data for which this service is the source of truth>
OUT_OF_SCOPE: <explicitly forbidden responsibilities>
PRIMARY_STORAGE: <PostgreSQL | none | another explicitly approved store>
SECONDARY_STORAGE: <Redis or none; explain exact responsibility>
EXTERNAL_DEPENDENCIES: <services, RPC providers, nodes, gateways>
AUTH_POLICY: <owned here | external Auth Service | not yet integrated>
REALTIME_POLICY: <HTTP only | HTTP + WebSocket>
SPECIAL_INVARIANTS: <domain invariants that must never be violated>
FIRST_PRODUCTION_SCOPE: <what must exist before the service is frozen>
```

The Service Profile is not decorative documentation. It defines the service boundary.

Do not silently add responsibilities absent from the profile.

When a new requirement conflicts with an older one:

1. state the conflict;
2. apply the newest explicit requirement;
3. update this file and affected documentation;
4. remove obsolete contradictory rules.

Priority:

```text
1. latest explicit user requirement
2. completed Service Profile
3. this AGENTS.md
4. older repository decisions
```

---

# Template Identity Variable

The pristine template contains one canonical editable Python variable:

```python
# app/service.py
SERVICE_NAME: Final[str] = "templateService"
```

The same module derives, rather than independently hardcodes:

```text
SERVICE_SLUG
SERVICE_ENV_PREFIX
SERVICE_ERROR_PREFIX
```

`SERVICE_NAME` is the runtime source of truth for:

- FastAPI title;
- OpenAPI `x-pokerlost-service.id`;
- root and OpenAPI operation IDs;
- CLI name and help;
- Logfire service name;
- PostgreSQL `application_name`.

Before service-specific implementation begins:

1. change `SERVICE_NAME` or run the repository initializer;
2. confirm the derived slug and environment prefix;
3. complete the Service Profile;
4. align non-Python package, Helm, image, and project metadata;
5. generate a fresh lock file;
6. only then add the first domain vertical slice.

Do not scatter separate Python literals for the service name.

---

# Pristine TEMPLATE Scope

The pristine TEMPLATE repository contains only reusable service infrastructure:

```text
FastAPI application factory
lifespan-owned resources
Pydantic Settings
request/correlation context
universal ApplicationResponse
central error mapping
RPC/OpenAPI contract generation
public root endpoint
wrapped JSON OpenAPI endpoint
async SQLAlchemy/PostgreSQL foundation
Alembic foundation without business revisions
repository/result-reader primitives
Logfire configuration/instrumentation
Typer local CLI
Gunicorn production command
Docker
Helm/kind values
uv/Ruff/mypy/pre-commit tooling
```

The pristine template must not contain:

```text
service-domain entities
business handlers
concrete ORM tables
business migrations
users or accounts
roles or permissions
JWT issuance or verification
sessions or refresh tokens
service credentials
OAuth token endpoints
OpenAPI contract registry
financial, poker, crypto, or profile logic
audit/rate-limit business state
background workers
```

After the template is initialized for a concrete service, service-specific tasks may add only the
capabilities justified by the completed Service Profile.

---

# Communication and Repository Language

- Communicate with the repository user in Russian unless they request another language.
- Keep repository-owned code documentation in English:
  - module/class/function/method docstrings;
  - meaningful comments;
  - OpenAPI summaries and descriptions;
  - settings descriptions;
  - CLI help;
  - developer-facing logs;
  - README and deployment documentation.
- Use concise PEP/reStructuredText-style docstrings.
- Do not add Google-style `Args:`, `Returns:`, or `Raises:` sections.
- Do not add docstrings that merely repeat the symbol name.

---

# Scope Discipline

Before changing the repository:

1. read root `AGENTS.md` fully;
2. inspect the current tree;
3. inspect only files relevant to the task;
4. preserve unrelated user changes;
5. avoid repository-wide cosmetic rewrites;
6. review the final diff;
7. report assumptions and incomplete checks honestly.

Do not:

- perform unrelated refactoring;
- invent paths without inspecting the repository;
- add infrastructure without a current requirement;
- add a dependency because it may be useful later;
- perform destructive Git operations;
- change branches, commit, merge, or push unless explicitly requested;
- claim a command passed when it was not run.

A new abstraction must own an independent responsibility.

Do not create an interface, base class, wrapper, mapper, provider alias, helper, service, registry,
or DTO merely to rename another object, forward one call, or provide theoretical flexibility.

---

# Default Technology Stack

Unless the Service Profile explicitly requires another architecture, use:

```text
Python >= 3.12
FastAPI
Pydantic v2
Pydantic Settings
SQLAlchemy 2.x async ORM
asyncpg
PostgreSQL
Alembic
Typer
Pydantic Logfire
Gunicorn
uvicorn-worker
Uvicorn for local development
Docker
Helm
kind for local Kubernetes development
uv
Ruff
mypy
pre-commit
```

Do not add by default:

```text
Redis
MongoDB or another NoSQL store
another ORM
raw-SQL-only persistence
message brokers
Celery
another web framework
a second logging/observability stack
JWT/JOSE libraries
password hashing libraries
OAuth authorization-server frameworks
```

Auth/crypto/realtime dependencies are added only when the Service Profile and an explicit stage
require them.

---

# Python Conventions

- Support Python 3.12 and newer.
- Ruff and mypy target Python 3.12.
- Maximum line length: 99.
- Ruff Formatter is the only formatter.
- Every maintained project-owned Python module begins with:

```python
"""English module documentation."""

from __future__ import annotations
```

- Use Python 3.12 PEP 695 generics and `type` aliases where supported.
- Avoid `Any`, broad `cast()`, broad `# type: ignore`, and reflection for known fields.
- Do not mutate known fields through `setattr`, `vars`, `__dict__`, or `object.__setattr__`.
- Use canonical acronym capitalization:
  - `API`;
  - `HTTP`;
  - `UUID`;
  - `SQLAlchemy`;
  - `OAuth2`;
  - `OpenAPI`.
- Choose collections by meaning:
  - `list` for ordered materialization;
  - `set` for mutable uniqueness;
  - `frozenset` for immutable uniqueness;
  - `tuple` only for a fixed semantic sequence or library contract.

---

# Source Root, Packages, and Imports

Use:

```text
app/
```

as the Python source root. `app` is not an import prefix.

Correct:

```python
from api...
from application...
from configuration...
from domain...
from observability...
from persistence...
from service import SERVICE_NAME
```

Forbidden:

```python
from app.api...
from app.application...
```

Local commands use:

```bash
PYTHONPATH=app
```

Containers use:

```text
PYTHONPATH=/service/app
```

Never mutate `sys.path`.

Every Python package under `app/` contains `__init__.py`.

Use relative imports inside the current package. Imports crossing top-level architectural packages
are absolute.

Parent-climbing imports are forbidden:

```python
from ..base import ConflictError
```

Use:

```python
from application.errors import ConflictError
```

`__init__.py` is an intentional public facade, not an export dump.

---

# Architecture

The default request path is:

```text
HTTP Request
    ->
FastAPI action router
    ->
Pydantic Request
    ->
Command or Query
    ->
Handler
    ->
shared service only when genuinely reused
    ->
SQLAlchemy entity repository
or SQLAlchemy read query adapter
    ->
PostgreSQL
```

Dependencies are assembled at the API boundary.

Direction:

```text
api composition -> application + persistence
application     -> persistence + domain
persistence     -> domain
configuration / observability -> composition root
```

Persistence must not import application operations or API schemas.

Do not create circular imports.

---

# Recommended Source Layout

Adapt this layout to the concrete service. Do not create speculative empty feature directories.

```text
app/
    service.py

    api/
        application.py
        lifespan.py
        openapi.py
        request_context.py
        resources.py
        routes.py

        dependencies/
            __init__.py
            database.py
            resources.py
            settings.py

        errors/
            __init__.py
            application.py
            configure.py
            database.py
            http.py
            unexpected.py
            validation.py

        routers/
            root.py
            openapi_document/
                __init__.py
                router.py
            <feature>/
                __init__.py
                router.py
                dependencies.py
                <action>.py

        schemas/
            base/
            orm/
            requests/
            responses/

        types/

    application/
        errors/
        <feature>/
            __init__.py
            <operation>/
                __init__.py
                command.py or query.py
                handler.py

    configuration/
    domain/
        enums/
        types/
        value_model.py

    observability/

    persistence/
        database/
            base.py
            session.py
            mixins/
            models/
            result_readers/
        repositories/
        queries/
        projections/

    cli/
```

One public request, response, command, query, handler, error, projection, or ORM entity per file is
preferred when it improves navigation.

Do not create giant `services.py`, `models.py`, `errors.py`, `utils.py`, or `common.py` dumping
grounds.

---

# Naming Contract

## SQLAlchemy ORM

Every concrete SQLAlchemy entity class ends with:

```text
Model
```

Every concrete ORM entity file ends with:

```text
_model.py
```

Examples:

```text
AccountModel          -> account_model.py
LedgerEntryModel      -> ledger_entry_model.py
TablePositionModel    -> table_position_model.py
```

Shared abstract bases are the limited exceptions:

```text
Base
UUIDModel
CreatedAtMixin
TimestampMixin
UUIDPrimaryKeyMixin
```

Mixin files end with `_mixin.py`.

## API requests

Concrete request class:

```text
SomethingRequest
```

File:

```text
something_request.py
```

## API responses

Every concrete public result schema ends with:

```text
Response
```

Every response file ends with:

```text
_response.py
```

This applies to both:

```text
api/schemas/responses/
api/schemas/orm/
```

Examples:

```text
AccountResponse             -> api/schemas/orm/account_response.py
AccountsPageResponse        -> api/schemas/responses/accounts_page_response.py
OpenApiDocumentResponse     -> api/schemas/responses/openapi_document_response.py
ApplicationResponse         -> api/schemas/responses/application_response.py
```

The shared ORM response base is:

```text
ORMResponse
```

in:

```text
api/schemas/orm/orm_response.py
```

Do not name public transport contracts `*Schema`, `*DTO`, or `*Model`.

## Internal values

Use semantic suffixes:

```text
Command
Query
Result
Projection
Summary
Page
Error
Handler
Repository
```

Internal application `Result` is not an API `Response`.

---

# HTTP RPC API Standard

The platform API is intentionally RPC-like.

Use:

```text
POST
GET
```

- Every command or query requiring input uses `POST` and exactly one documented Pydantic body.
- `GET` is reserved for parameterless endpoints.
- Do not use `PUT`, `PATCH`, or `DELETE`.
- Do not put business identifiers in path parameters or custom business headers.

Paths use dotted camelCase:

```text
/accounts.createAccount
/accounts.getAccount
/holds.reserveHold
/tablePositions.cashOut
```

Canonical form:

```text
/{namespace}.{method}
```

The only path exception is:

```text
GET /
```

which is the parameterless service root.

No other path exceptions exist. OpenAPI is exposed as:

```text
GET /openapi.get
```

not `/openapi.json` or `/.well-known/...`.

Every route decorator places `path=` first.

Every endpoint declares:

- path;
- concrete `response_model` based on `ApplicationResponse`;
- status code;
- English summary;
- English description;
- stable operation ID;
- documented error responses;
- logical tag;
- explicit OpenAPI security.

---

# OpenAPI operation IDs and scopes

Every endpoint declares one stable operation ID.

Convention:

```text
<SERVICE_NAME>.<namespace>.<method>
```

Examples:

```text
accountService.accounts.getAccount
virtualMoney.holds.reserveHold
pokerService.tablePositions.cashOut
```

Root:

```text
/
-> <SERVICE_NAME>.root
```

For a non-root RPC path:

```text
/accounts.getAccount
-> <SERVICE_NAME>.accounts.getAccount
```

A protected operation's canonical OAuth2 scope is exactly its operation ID.

Never confuse OpenAPI `operationId` with a business `operation_id`/idempotency key.

---

# Router Architecture

One router package represents one logical API area. Each action lives in a focused file.

Example:

```text
api/routers/accounts/
    __init__.py
    router.py
    dependencies.py
    create.py
    get.py
```

The base router imports router objects explicitly:

```python
from .create import router as create_router
from .get import router as get_router
```

Routers are thin. They:

1. accept a Request;
2. receive a Handler through DI;
3. map Request to Command/Query;
4. call `handler.execute(...)`;
5. return a `HandlerResult` dictionary matching the declared response.

Routers do not:

- receive or use `AsyncSession` directly;
- build SQLAlchemy statements;
- commit or roll back;
- calculate business state;
- implement idempotency;
- perform persistence mapping.

---

# Universal ApplicationResponse Contract

Every HTTP API method returns data through exactly one public envelope:

```python
class ApplicationResponse[ResultT](ResponseModel):
    ok: bool
    result: ResultT | None
    error: str | None
    error_message: str | None
```

There are no raw API payload exceptions.

This includes:

```text
service root
OpenAPI JSON publication
OAuth2 protocol endpoints if the service owns them
JWKS if an Auth Service owns it
business RPCs
handled validation/application/database/framework/unexpected errors
```

Success:

```json
{
  "ok": true,
  "result": {}
}
```

Failure:

```json
{
  "ok": false,
  "result": null,
  "error": "STABLE_ERROR_CODE",
  "errorMessage": "Safe English message"
}
```

Do not include HTTP status, request ID, correlation ID, trace ID, or transport metadata in the
body. Request/correlation identifiers are response headers and telemetry fields.

Handlers return explicit dictionaries:

```python
return {
    "ok": True,
    "result": result,
}
```

Do not create response factories/builders or call `.model_dump()` only for serialization.

All `APIRoute` objects included in OpenAPI must declare `ApplicationResponse` or a parameterized
`ApplicationResponse[...]` as their response model. The application startup/OpenAPI contract
validation must fail fast if a route violates this rule.

Central exception handlers may construct `JSONResponse`, but its body must match
`ApplicationResponse` exactly.

---

# Pydantic Model Boundaries

Use Pydantic v2 for:

- HTTP Requests;
- ORM Responses;
- calculated/composite Responses;
- Commands;
- Queries;
- structured application Results;
- read Projections;
- pagination values;
- domain value objects;
- Settings.

Do not use Pydantic for:

- SQLAlchemy mapped entities;
- repositories;
- handlers/services;
- engine/session/runtime resources.

## API base models

`APIModel` owns:

```text
camelCase aliases
extra=forbid
hide_input_in_errors
populate_by_name
serialize_by_alias
validate_default
```

`ResponseModel` is immutable.

`ORMResponse` is immutable, inherits the response behavior, and alone enables:

```python
ConfigDict(from_attributes=True)
```

Requests use secret-aware field types for passwords/tokens/credentials when applicable.

## Internal structured values

Use one immutable alias-free `ValueModel` for Commands, Queries, Results, Projections, and domain
value objects.

Do not add transport aliases to application/domain values.

---

# Dependency Injection

Composition occurs at the API boundary.

Every FastAPI dependency is declared once as a PEP 695 `type` alias:

```python
type DatabaseSession = Annotated[
    AsyncSession,
    Depends(get_database_session, scope="function"),
]
```

Use aliases in route/provider signatures. Do not repeat inline `Annotated[..., Depends(...)]`.

Shared baseline aliases:

```text
ApplicationResourcesDep
SettingsDep
DatabaseSession
```

Feature dependencies stay feature-local.

Do not create a giant global dependency container or service locator.

Request/correlation headers are handled by middleware, not FastAPI `Header` dependencies.

---

# Database Transaction Lifecycle

The default HTTP transaction boundary is one request dependency:

```python
async with session_factory.begin() as session:
    yield session
```

Semantics:

```text
normal dependency exit -> commit
exception              -> rollback
finally                -> close
```

Routers, handlers, repositories, and query adapters do not call:

```text
begin
commit
rollback
```

Do not add a Unit of Work over this request transaction dependency.

CLI/operator commands own an explicit composition transaction using `session_factory.begin()` and
reuse application handlers; they do not use FastAPI dependencies.

Security/audit use cases that must commit failure state require explicit application semantics,
not accidental exception-driven rollback.

---

# SQLAlchemy Database Structure

Use:

```text
persistence/database/
    base.py
    session.py
    mixins/
    models/
    result_readers/
```

## Base and mixins

Keep:

```text
Base
UUIDModel
CreatedAtMixin
TimestampMixin
UUIDPrimaryKeyMixin
```

`UUIDPrimaryKeyMixin` uses PostgreSQL:

```sql
gen_random_uuid()
```

Do not use Python `uuid4()` as the normal ORM primary-key default.

`Base.metadata` uses one deterministic naming convention for PK/FK/UQ/CK/IX names.

## ORM models

- one concrete `*Model` per `*_model.py` file;
- SQLAlchemy 2 typed mappings;
- `Mapped[T]` and `mapped_column`;
- explicit constraints/indexes;
- typed relationships only when useful;
- loading policy such as `lazy="raise"`;
- no Active Record methods.

ORM classes do not contain persistence operations.

## Constraints

Critical invariants are also protected by PostgreSQL:

```text
unique business identifiers
foreign keys
valid states
race-sensitive uniqueness
bounded values
one-active-resource constraints
```

Pydantic validation does not replace database constraints.

Do not rewrite accepted historical migrations for style.

The pristine template contains no business table and no empty baseline revision.

---

# Repository and Read Query Split

## Entity repositories

`persistence/repositories/` contains entity/aggregate persistence adapters.

Repository reads return ORM models or natural scalar outcomes.

Repositories do not return:

```text
API responses
raw Row/RowMapping
dictionaries indexed by IDs
Pydantic read projections
```

## Read query adapters

`persistence/queries/` contains optimized multi-table read operations.

They return typed immutable Projections from `persistence/projections/`.

Default CQRS-lite split:

```text
Repository -> ORM entity persistence
Query adapter -> optimized typed read projection
```

Do not call query adapters repositories.

---

# Base Repositories and Result Readers

Use one small:

```text
SQLAlchemyRepository
```

It owns only:

```text
request AsyncSession
scalar execution
projection execution
```

Use:

```text
SQLAlchemyEntityRepository[ModelT]
```

for normal UUID entities. Concrete repositories bind:

```python
model = AccountModel
```

not an instance `_model` constructor argument.

The base must not become generic CRUD.

All scalar extraction is centralized in:

```text
SQLAlchemyScalarResultReader[T]
```

All projection mapping is centralized in:

```text
SQLAlchemyProjectionResultReader[T]
```

Concrete repositories/query adapters do not directly call:

```text
scalar
scalar_one
scalar_one_or_none
scalars
mappings
tuples
```

---

# Persistence Writes

Use explicit SQLAlchemy DML:

```text
INSERT
UPDATE
DELETE
RETURNING
ON CONFLICT
SELECT ... FOR UPDATE
```

Prefer one statement and one result.

Do not use as normal repository write flow:

```text
session.add
add_all
flush
refresh
```

Do not hide read-after-write.

Repositories return natural outcomes and let Handlers map expected conflicts/not-found states to
application errors.

Never parse database exception strings.

---

# Pagination

Use bounded keyset/cursor pagination for large or immutable histories.

Do not use unbounded list endpoints.

Do not build a generic pagination framework before a real use case exists.

---

# Errors

Application errors are transport-independent and expose only:

```text
stable machine error code
safe English public message
```

Baseline semantic categories:

```text
ApplicationError
AuthenticationError when applicable
ForbiddenError
NotFoundError
ConflictError
InvalidOperationError
IntegrityError
RateLimitedError when applicable
```

API mapping:

```text
authentication -> 401
forbidden      -> 403
not found      -> 404
conflict       -> 409
invalid op     -> 422
rate limited   -> 429
integrity      -> safe 500
database unavailable -> 503
```

All handled errors return `ApplicationResponse`.

Do not expose exception text, SQL, identifiers, tokens, secrets, or internal state.

Generic baseline error codes derive from `SERVICE_ERROR_PREFIX`, not a copied service-specific
prefix.

---

# Settings

Use one root:

```python
class Settings(BaseSettings):
    ...
```

Nested groups inherit one immutable strict `SettingsModel`.

Baseline groups:

```text
ApplicationSettings
DatabaseSettings
HTTPSettings
LogfireSettings
```

`SettingsConfigDict.env_prefix` derives from `SERVICE_ENV_PREFIX` in `app/service.py`.

Use Settings for deployment/runtime values:

```text
database URL and pool settings
environment
service version
local HTTP host/port
Logfire settings
```

Keep protocol/domain invariants in code.

Do not:

```text
scatter os.getenv
call load_dotenv in application modules
instantiate Settings at arbitrary import points
print secrets
store secrets in repr
put Gunicorn process tuning in Pydantic Settings
```

Critical production configuration fails fast.

---

# Request Context

Middleware owns:

```text
server-generated request_id
validated correlation_id
request.state
Logfire baggage
X-Request-ID response header
X-Correlation-ID response header
```

Client `X-Request-ID` never becomes the server request ID.

The request-context layer is the single owner of these response headers, including sanitized 500
responses.

Do not inject request/correlation IDs through `Header(...)` dependencies.

---

# Observability

Use Pydantic Logfire as the single observability implementation.

Configure once at composition time.

Instrument:

```text
FastAPI
concrete SQLAlchemy engine
```

Do not create a custom logger, second OpenTelemetry stack, or custom ContextVar framework.

Disable capture of headers, parsed endpoint arguments, send/receive bodies, and request payloads by
default.

Scrub at minimum:

```text
authorization
cookie
credential
database URL / DSN
password
private key
secret
token
```

Never claim telemetry is durable audit.

---

# OpenAPI JSON and OAuth2 Scope Contract

OpenAPI is a machine-readable platform contract.

Built-in endpoints are disabled:

```text
/openapi.json
/docs
/redoc
```

The service exposes generated JSON only through:

```text
GET /openapi.get
```

wrapped as:

```text
ApplicationResponse[OpenApiDocumentResponse]
```

YAML OpenAPI output is unsupported in the baseline.

Every service contract contains exactly:

```json
{
  "x-pokerlost-service": {
    "id": "<SERVICE_NAME>"
  }
}
```

The extension contains only `id`.

## Public operations

Public operations declare explicit empty security:

```json
{
  "security": []
}
```

## Protected operations

OAuth2 is the only platform runtime RPC authorization primitive.

The canonical security scheme is named:

```text
OAuth2
```

Every protected operation requires exactly one scope equal to its operation ID:

```json
{
  "operationId": "accountService.accounts.getAccount",
  "security": [
    {
      "OAuth2": [
        "accountService.accounts.getAccount"
      ]
    }
  ]
}
```

Do not add:

```text
x-pokerlost-authz
roles in downstream API contracts
permissions arrays
custom Bearer metadata
implicit scope inheritance
wildcard scopes
```

Role/grade-to-scope policy belongs to the owning authorization/account-control architecture, not
individual downstream services.

The pristine template publishes the OAuth2 scheme and contains only public root/OpenAPI
operations. It does not implement token issuance, token verification, principals, roles, or scope
grants.

A concrete service adds runtime OAuth2 verification only after `AUTH_POLICY` is explicit.

## Contract fail-fast validation

Application/OpenAPI construction must validate:

```text
/ is the sole non-RPC path
non-root paths match /{namespace}.{method}
operationId matches SERVICE_NAME + path
operation IDs are unique
public operations have security=[]
protected operations require exactly their operationId scope
all API routes use ApplicationResponse
x-pokerlost-service.id equals SERVICE_NAME
```

Do not silently generate a contract that violates these rules.

---

# Authentication Ownership

The Service Profile must explicitly set `AUTH_POLICY`.

## Non-auth service

A non-auth service does not issue tokens or own human/service credentials.

Do not add:

```text
fake API keys
development tokens
local password/session tables
local scope grant databases
placeholder principals
```

It may later validate Auth Service tokens locally using the agreed OAuth2/JWT/JWKS contract.

## Auth service

Only a service whose profile says `AUTH_POLICY: owned here` may own:

```text
credential verification
token issuance
refresh/revocation
principal identity
scope grants
signing keys
JWKS
OAuth2 authorization-server behavior
security audit/rate limits
```

Those capabilities are not part of the generic template and must be implemented by explicit
service stages.

---

# Real-Time Services

If `REALTIME_POLICY: HTTP only`, do not add WebSocket infrastructure.

If `HTTP + WebSocket` is explicit:

```text
HTTP RPC -> commands/queries
WebSocket -> realtime snapshots/events
```

Define typed event envelopes, sequence/reconnect semantics, and source-of-truth ownership before
implementation.

Do not add long polling or Redis by default.

---

# CLI and Process Model

Use Typer as a small development/operator CLI.

Baseline command:

```text
<SERVICE_SLUG> run
```

It starts one Uvicorn development worker through:

```text
api.application:create_app
factory=True
```

Production uses direct Gunicorn with:

```text
uvicorn_worker.UvicornWorker
```

Do not use deprecated `uvicorn.workers.UvicornWorker`.

Production does not run through Typer.

Makefile remains a thin interface for:

```text
install
run
serve
format
lint
typecheck
pre-commit
db-upgrade
db-downgrade
db-revision
```

---

# Docker

Use a deterministic multi-stage build.

Requirements:

```text
Python 3.12+
locked dependencies
PYTHONPATH=/service/app
non-root UID/GID
read-only-friendly runtime
no .env
no secrets
no reload
no migrations at startup
exec-form Gunicorn startup
```

Do not combine migrations and server startup.

---

# Helm and kind

Use:

```text
deploy/helm/<service-slug>/
```

Use `SERVICE_SLUG` for Kubernetes/Helm technical names and `SERVICE_NAME` for human-facing metadata.

Baseline chart includes:

```text
Deployment
Service
ConfigMap
values.yaml
values-kind.yaml
```

Secrets are references to existing Kubernetes Secrets, never literal values or ConfigMap data.

Probes use:

```text
GET /
```

Do not add migrations/init jobs, ServiceAccount tokens, ingress, autoscaling, Redis, or external
operators without an explicit requirement.

Security baseline:

```text
runAsNonRoot
fixed UID/GID
allowPrivilegeEscalation=false
readOnlyRootFilesystem=true
drop ALL capabilities
RuntimeDefault seccomp
automountServiceAccountToken=false
```

---

# Documentation

README describes only implemented behavior.

The pristine template README must explain:

```text
how to initialize SERVICE_NAME
how to complete the Service Profile
current infrastructure-only scope
local setup
configuration
root/OpenAPI endpoints
commands
migrations
Docker/Helm
how to add the first vertical slice
```

Do not document hypothetical business features as implemented.

---

# Anti-Patterns

Do not add:

```text
Active Record ORM methods
GenericRepository CRUD framework
UnitOfWork over request transaction
ResponseFactory / ResponseBuilder
raw API payload exceptions to ApplicationResponse
REST resource paths in the RPC API
a second OpenAPI endpoint
service-name literals scattered across Python
concrete ORM classes without Model suffix
public response classes/files without Response/_response
inline repeated Annotated Depends declarations
repository mega-container
service locator
sys.path mutation
session.add/flush/refresh normal write flows
manual commit/rollback in handlers
hidden read-after-write
raw RowMapping contracts
exception-string parsing
hardcoded SQLSTATE lists
custom logger alongside Logfire
remote OpenAPI fetching
custom authorization metadata instead of OAuth2 scopes
role inheritance or admin bypass
```

---

# Tests and CI/CD

Tests and CI/CD are handled separately unless the user explicitly requests them.

Do not add or modify:

```text
unit/integration/E2E tests
fixtures
coverage
pytest configuration
GitHub Actions
GitLab CI
Jenkins
CI runners
automated deployment pipelines
```

Architecture must remain testable:

```text
explicit dependencies
deterministic business rules
injectable time/randomness when behavior depends on them
application logic executable without HTTP
external systems behind real adapter boundaries
```

---

# Codex Work Mode

Codex must:

1. read `AGENTS.md` first;
2. inspect the current tree;
3. make the smallest coherent diff;
4. preserve unrelated changes;
5. avoid global formatting unrelated files;
6. never claim unexecuted verification;
7. report assumptions and blockers;
8. show created/modified/deleted files;
9. not commit/push/merge/switch branches unless explicitly requested.

Do not automatically run expensive Docker/Helm/kind/PostgreSQL checks unless the task requires
them. When acceptance criteria require verification, run the relevant commands or state the exact
environment limitation.

---

# Completion Report

At the end of a Codex task, report in Russian:

1. implemented behavior;
2. architecture decisions;
3. public API changes;
4. migrations;
5. created files;
6. modified files;
7. deleted files;
8. dependency changes;
9. assumptions;
10. known limitations;
11. commands actually run and exact results;
12. commands intentionally not run;
13. manual verification instructions;
14. final readiness status.

Do not call a stage complete while mandatory acceptance criteria remain unfinished.
