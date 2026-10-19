# Pokerlost operation names

This specialization owns external Pokerlost operations. Python follows PEP 8; the generic
FastAPI template does not inherit this protocol. The SDK remains authoritative for existing
wire contracts; see [SDK compatibility](../SDK_COMPATIBILITY.md).

## Paths, identifiers and modules

A business operation uses `POST /getOperation` with explicit `operation_id="getOperation"`.
Its Python function is `get_operation`, in a flat `routers/get_operation.py` module. Use a
module-level `APIRouter(tags=["get"])` and ordinary FastAPI decorators, models and dependencies.
Do not add a routing framework, runtime route rewriting or a registry of operation strings.

| Responsibility | Example |
| --- | --- |
| External path and operation ID | `/getOperation`, `getOperation` |
| Python module and function | `get_operation.py`, `get_operation` |
| Logical verb tag | `get` |
| Request / response | `PokerlostRequest[Payload]`, `PokerlostResponse[Result]` |
| Authorization | Native `Security(..., scopes=[...])`, exact service-owned scopes |

Vue, Dart and generated SDK consumers retain the existing wire spelling. Do not derive
operation IDs from Python function names. Keep business IDs unique across the documents
combined by an SDK consumer; check the actual OpenAPI inventory before choosing a new name.

## Choose the verb by behavior

Use `get`, `list`, `create`, `update`, `replace`, `delete`, `set`, `assign`, `unassign`,
`issue`, `revoke`, `register`, `provision`, `start`, `stop` or `cancel` when it describes
the actual scenario. Tags group by that verb; they are documentation, not authorization.
Do not classify a call as read-only, retryable or idempotent from its name. In particular,
existing `getToken` issues credentials. Preserve `getToken`, `provisionHuman`,
`issueLoginGrant`, `replacePrincipalScopes` and their published payloads and scope strings.
An interface change requires an explicit migration and contract tests.

The public infrastructure exceptions remain `GET /` (`getRoot`), `GET /getOpenApi`
(`getOpenApi`), `GET /health/live` and `GET /health/ready`. Their existing tags and methods
remain stable. Health probes are omitted from the SDK OpenAPI document. Do not introduce
fake business routes merely to populate the pristine template.

## Verification and ownership

The generated foundation tests inspect the application's real routes and `/getOpenApi`.
A test-only `getOperation` router proves explicit operation ID, verb tag, POST and the SDK
envelopes through `with TestClient(app)`. It is never registered by a generated application.
Service-owned routes, models, scopes and application scenarios remain project-owned during
Copier updates. Add focused tests beside them and check actual combined SDK documents when
integrating another service. Keep business behavior and external I/O out of model validators.
