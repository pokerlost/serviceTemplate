# Pokerlost service foundation

The active Copier source is `composedTemplate/`, assembled from content-addressed FastAPI source and `foundationOverlay/`. The prior flat source remains in historical Git ref `7ee1232`; it is absent from the active worktree and does not define new renders.

The template version comes from `pyproject.toml`; `composition.toml` declares answers schema 1. `composition.lock.json` records the actual content identity, including the root `copier.yml` digest. Generated `.template-version.json` records the selected template version and full source commit through supported Copier metadata. The generated application owns its separate package version.

## 🧭 Generation and ownership

Copier 9.17.2 asks for `service_name` and derives `service_slug`, `service_env_prefix`, `database_name`, `projectName`, and a lowercase `packageName` once. New services require Python 3.14+ because the pinned `pypokerlost` SDK does. A generated wheel runs without neighboring template checkouts or a workspace `PYTHONPATH`. The default needs no DSN, remote telemetry credential, outbound token, or production verifier. PostgreSQL wiring is optional through `withPersistence=true`; it adds no business table, migration revision, or startup migration.

The Python base owns package metadata, quality defaults, and shared development structure. The FastAPI base owns settings, factory, lifespan, process resources, HTTP health, request correlation, and optional DB transaction wiring. This layer owns `PokerlostResponse` root, raw `/getOpenApi`, exact OAuth scope/verifier boundary, pinned SDK source, and service-specific documents. The generated project owns `SERVICE.md`, `PROJECT.md`, routes, scopes, settings policy, adapters, migrations, and business behavior. Copier updates must not silently overwrite project-owned content.

The shared HTTP error handlers sanitize validation, framework, readiness, and unexpected failures. This layer specializes their body to `PokerlostResponse[None]` with the service error prefix; it never echoes submitted values, DSNs, or exception text.

## 🔌 Public infrastructure and future operations

The pristine service registers `GET /` (`getRoot`, `PokerlostResponse[None]`), `GET /getOpenApi` (`getOpenApi`, unmodified FastAPI OpenAPI), `/health/live`, and `/health/ready`. It registers no business endpoint. A future operation uses one service-local unique lower camelCase `POST /<operationId>` with `PokerlostRequest[Payload]` and `PokerlostResponse[Result]`. Do not introduce generic REST aliases or an invented operation to populate the scaffold.

Protected calls receive `Authorization: Bearer <token>` outside the body. Explicit gateway clients also send the noncredential routing header `x-pokerlost-serviceId`; direct service clients retain their previous default. A route declares a non-empty exact set of service-owned dotted lower camelCase scopes. A local verifier must verify the token and exact service audience; the pristine verifier is absent and fails closed. The SDK owns HTTP transport, canonical response decoding, explicit retry, token-store/refresher ports, and one narrow expired-token refresh. It is not a UI or realtime client. [SDK_COMPATIBILITY.md](SDK_COMPATIBILITY.md) owns the detailed SDK contract and pinned revision.

## 🔒 Failure and lifecycle boundaries

The factory reads settings only when called and opens no network connection at import. Lifespan creates/disposes enabled resources per worker, including after partial startup failure. Liveness does not query dependencies; readiness checks only enabled required resources with a timeout. The optional request session dependency owns commit/rollback before the response. Do not share an `AsyncSession` across tasks, hold one through streaming/WebSocket/background work, or call an outbound SDK inside an open DB transaction.

This foundation does not provide business handlers, a fake verifier, payments, game orchestration, token storage, a provider SDK, or outbound credentials. New renders include technical HTTP/lifecycle tests, CI source checks, and a backend Dockerfile. Private SDK checks require separately approved narrow access and a reviewed execution boundary. Existing tests/workflows in older projects are not removed by this source migration.

## 🧪 Tests and deployment candidates

The inherited Python/FastAPI foundation owns coverage configuration, installed-package tests,
resource cleanup, PostgreSQL transaction integration, the multi-stage Docker build, Compose test
services and the managed Helm chart. This specialization adds canonical response and authorization
assertions. `tests/foundation/` is managed; project seed tests, `SERVICE.md`, `PROJECT.md`, settings,
scopes, migrations and `deploy/values.yaml` remain project-owned during updates. The generic chart
is generated from the pinned FastAPI snapshot, never edited as an independent implementation.

The private runtime workflow uses the approved solo-owner/full-SHA policy described in
[technical verification](docs/testing.md). Ordinary PR source checks have no SDK secret and do
not claim B1 runtime acceptance. Manual dispatch requires the actual private build to pass.
The trusted default workflow and source commit have separate full-SHA admission pins. An exact
integrated source remains admissible after its PR closes; a changed HEAD requires new review.
The existing SDK-only App installation is unchanged. Reassess the model if another writer is added.

The approved candidate builds wheel/sdist and installed-wheel test/runtime targets using one
BuildKit graph. Its cache is scoped to the private consumer repository, platform and target, with
normal GitHub branch isolation. Fresh tests and PostgreSQL run after cache restoration. The tested
runtime image is loaded into disposable Kind, migrated, probed, scaled and rolled back; it is also
saved as a private workflow artifact. A Docker image ID is a local identity, not a registry manifest
digest. No registry, release or remote cluster publication is implicit.

Service-specific published Make commands can remain in `Makefile.local`, included by the shared
Python Makefile. Local host/port/reload choices use the inherited FastAPI command options; the
runtime image does not inherit them. Full persistence testing starts a fresh integration coverage
measurement, includes owner `tests/*_integration.py` cases, then appends isolated tests and writes
advisory reports; test/build/type/report errors still fail. Test assets preserve tools/migrations while `src/` is excluded and installed origin
is asserted inside pytest. A source checkout cannot satisfy the installed-wheel assertion.

## Local source-only SDK build

A private bare SDK source cache can replace the named `sdk-source` Docker build context. Use `--build-context sdk-source=/private/state/sdk-source --build-arg SDK_SOURCE_MODE=local`. The context contains only `pypokerlost.git`, created with `git clone --bare --no-hardlinks` from the reviewed checkout; no SSH configuration, token, working tree or credentials. The locked full SDK Git revision remains authoritative. Missing commits fail the frozen sync. Only the builder contains the source cache; the runtime receives the installed environment. Remote mode continues to require the existing SDK-only BuildKit secret. platformInfra owns preparation, orchestration and receipts. This does not change B1 App admission or trusted-workflow policy.
