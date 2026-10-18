# Pokerlost service foundation

The active Copier source is `composedTemplate/`, assembled from content-addressed FastAPI source and `foundationOverlay/`. The prior flat source remains in historical Git ref `7ee1232`; it is absent from the active worktree and does not define new renders.

The current derivative worktree declares template version `0.2.0.dev0` and answers schema 1 in `composition.toml`; its actual content identity is in `composition.lock.json`, including the root `copier.yml` digest. These local identifiers are not a published tag or release.

## 🧭 Generation and ownership

Copier 9.17.2 asks for `service_name` and derives `service_slug`, `service_env_prefix`, `database_name`, `projectName`, and a lowercase `packageName` once. New services require Python 3.14+ because the pinned `pypokerlost` SDK does. A generated wheel runs without neighboring template checkouts or a workspace `PYTHONPATH`. The default needs no DSN, remote telemetry credential, outbound token, or production verifier. PostgreSQL wiring is optional through `withPersistence=true`; it adds no business table, migration revision, or startup migration.

The Python base owns package metadata, quality defaults, and shared development structure. The FastAPI base owns settings, factory, lifespan, process resources, HTTP health, request correlation, and optional DB transaction wiring. This layer owns `PokerlostResponse` root, raw `/getOpenApi`, exact OAuth scope/verifier boundary, pinned SDK source, and service-specific documents. The generated project owns `SERVICE.md`, `PROJECT.md`, routes, scopes, settings policy, adapters, migrations, and business behavior. Copier updates must not silently overwrite project-owned content.

The shared HTTP error handlers sanitize validation, framework, readiness, and unexpected failures. This layer specializes their body to `PokerlostResponse[None]` with the service error prefix; it never echoes submitted values, DSNs, or exception text.

## 🔌 Public infrastructure and future operations

The pristine service registers `GET /` (`getRoot`, `PokerlostResponse[None]`), `GET /getOpenApi` (`getOpenApi`, unmodified FastAPI OpenAPI), `/health/live`, and `/health/ready`. It registers no business endpoint. A future operation uses one globally unique lower camelCase `POST /<operationId>` with `PokerlostRequest[Payload]` and `PokerlostResponse[Result]`. Do not introduce generic REST aliases or an invented operation to populate the scaffold.

Protected calls receive only `Authorization: Bearer <token>` outside the body. A route declares a non-empty exact set of service-owned dotted lower camelCase scopes. A local verifier must verify the token and exact service audience; the pristine verifier is absent and fails closed. The SDK owns HTTP transport, canonical response decoding, explicit retry, token-store/refresher ports, and one narrow expired-token refresh. It is not a UI or realtime client. [SDK_COMPATIBILITY.md](SDK_COMPATIBILITY.md) owns the detailed SDK contract and pinned revision.

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

The private runtime workflow requires a full reviewed SHA, a private consumer repository and an
existing `sdk-build` environment with a required reviewer; the owner can be that reviewer. Place
SDK App secrets only in that environment. The SDK-only App has `Contents: read` solely for
`pokerlost/pypokerlost`; the workflow handles the actual cross-owner accountsService explicitly.
No secret is provided to ordinary PR jobs. The required runtime gate fails when private verification
is skipped or blocked. The template cannot configure the environment or App by itself.

The approved candidate builds wheel/sdist and installed-wheel test/runtime targets using one
BuildKit graph. Its cache is scoped to the private consumer repository, platform and target, with
normal GitHub branch isolation. Fresh tests and PostgreSQL run after cache restoration. The tested
runtime image is loaded into disposable Kind, migrated, probed, scaled and rolled back; it is also
saved as a private workflow artifact. A Docker image ID is a local identity, not a registry manifest
digest. No registry, release or remote cluster publication is implicit.
