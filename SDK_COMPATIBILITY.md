# serviceTemplate ↔ pypokerlost compatibility

This is the canonical maintainer contract and verification procedure for the generated server
template. Service-author guidance belongs in generated `docs/api/operation-contract.md`,
`docs/api/application-response.md`, and `docs/api/openapi-and-sdk.md`; short normative constraints
belong in generated `AGENTS.md`.

## Authoritative SDK revision

The compatibility work on 2026-08-29 verified the private
[`pokerlost/pypokerlost`](https://github.com/pokerlost/pypokerlost) `origin/main` revision:

```text
remote:               git@github.com:pokerlost/pypokerlost.git
distribution version: 0.2.0
commit:               8ca9d7153a99f57149364e0b860c319b02cac602
pin status:            verified on origin/main
generator version:    1.1.0
Python:               >=3.14
```

The generated-service dependency pins that exact full commit SHA. Local and remote SDK SHAs were
confirmed identical before the template pin was updated. The SDK implementation wins over stale
prose. Never substitute a sibling path, absolute path, `file://` source, embedded credential,
unverified index, or floating branch.

## Compatibility boundary

| Contract | SDK implementation | Generated-service requirement |
| --- | --- | --- |
| Python and style | `pyproject.toml` | Python >=3.14, Ruff `py314`, mypy 3.14, line length 100, Python 3.14 images |
| SDK installation | distribution `pypokerlost` | Verified private SSH source pinned to one full pushed commit SHA |
| API operation | `pypokerlost/types/operation.py` | `^[a-z][A-Za-z0-9]*\.[a-z][A-Za-z0-9]*$` |
| HTTP method | `pypokerlost/types/operation.py` | Only GET, POST, PUT, PATCH, DELETE; POST default |
| Runtime URL | `pypokerlost/client/api_server.py` | One API base plus `/<operation>` |
| Request objects | `pypokerlost/client/request/` | `Request`, `RequestBuilder`, and `RequestOptions` |
| Request serialization | `pypokerlost/client/request/request_builder.py` | Alias-free `snake_case` fields and `exclude_unset=True` |
| Request body | `scripts/generate_methods.py` | One named typed JSON object, or no body when parameterless; no parameters |
| Wire envelope | `pypokerlost/client/response/response.py` | Exact four fields/defaults/invariants; no extensions |
| Response decoding | `pypokerlost/client/response/response_handler.py` | API, protocol, and decode errors remain distinct |
| Publication endpoint | `scripts/generate_methods.py` | Configurable wrapped operation through `--openapi-operation`; default `openapi.get` |
| System paths | `scripts/generate_methods.py` | `/` and the configured publication path; no generated methods |
| OpenAPI document | `scripts/generate_methods.py` | OpenAPI 3.1.x and SemVer `info.version` |
| Service metadata | `scripts/generate_methods.py` | Exactly `x-pokerlost-service: {id: SERVICE_NAME}` |
| Generated layout | `scripts/generate_methods.py` | `pypokerlost/types/<service>/` and `pypokerlost/methods/<service>/` |
| Runtime target/lifecycle | `pypokerlost/client/` | One explicit `APIServer` per client/session and deterministic close |

The relevant public imports are:

```python
from pypokerlost import Client, OpenAPIExtra, PokerlostMethod, Response
from pypokerlost.client.api_server import APIServer
from pypokerlost.client.request import Request, RequestBuilder, RequestOptions
from pypokerlost.client.response import ResponseHandler
from pypokerlost.types import APIOperation, HTTPMethod
```

Service identity and operation identity are separate. `x-pokerlost-service.id` retains the Copier
`service_name`, including possible uppercase letters. Business operation IDs never derive directly
from it. The root system operation uses the lowercase `service_slug` namespace.

## Server contract

Canonical business API operation:

```text
operation = namespace.someOperation
path      = /<same operation>
request   = named closed typed JSON body, absent only when parameterless
success   = ApplicationResponse[<SemanticName>Response]
errors    = ApplicationResponse[None]
```

The operation ID has exactly two segments and one dot; each segment starts with a lowercase ASCII
letter and otherwise contains only ASCII letters and digits. Each business route module declares
one `OPERATION` constant and derives both decorator values from it.
Application-owned JSON is alias-free `snake_case`. A request schema is `<SemanticName>Request`, a
result schema is `<SemanticName>Response`, and typed nested objects are named closed components.
OpenAPI parameters and `Body(embed=True)` are not part of PokerLost operation transport. A `GET` with
input still uses JSON content.

All numeric 2xx responses for one operation have compatible JSON schemas. Request-body operations
explicitly publish `422` as `ApplicationResponse[None]`; expected 4xx/5xx use the same envelope so
FastAPI never advertises its default validation body as the public contract.

The local `ResponseModel` config is exactly:

```python
ConfigDict(
    extra="forbid",
    frozen=True,
    hide_input_in_errors=True,
    strict=True,
    validate_default=True,
)
```

The local `ApplicationResponse` has exactly `ok`, `result`, `error`, and `error_message`. `ok` is
required; the other three fields default to `None`. On success, both error fields are null. On
failure, result is null and both error fields are non-null. The schema has exactly four properties
and `additionalProperties: false`.

OpenAPI generation remains a thin `fastapi.openapi.utils.get_openapi` customization with cached
`application.openapi_schema`. It emits OpenAPI 3.1.0 and adds only:

```yaml
x-pokerlost-service:
  id: <SERVICE_NAME>
```

The public endpoint wraps that document in `ApplicationResponse`; built-in OpenAPI/docs URLs stay
disabled. Authorization declarations are service-specific FastAPI metadata and are not part of the
required template-to-generator subset; the wrapper preserves them without mutation.

## Supported generator subset

Reachable schemas may use named typed objects, arrays, typed/JSON-value dictionaries where
supported, string/integer/finite number/boolean/null, UUID/date/date-time/time, scalar enum/const,
nullable unions, supported `anyOf`/`oneOf`, object-only `allOf`, supported bounds/patterns, and
local component references.

The generator rejects external/relative refs, OpenAPI parameters, free-form top-level request
bodies, inline nested objects, unsupported media types or reachable JSON Schema keywords, invalid
field names, method-model or generated-name collisions, malformed/raw success envelopes, and
incompatible multiple 2xx schemas. Do not duplicate its complete reserved-name set or parser in
this repository.

The generator is repository-only development tooling: the runtime distribution installs the
`pypokerlost` package but no generator console command or `scripts/` package. Generator checks use
an authoritative SDK checkout or ephemeral copy; runtime client checks use the generated service's
installed dependency.

## Mandatory compatibility probe

Use actual Copier 9.17.2 and the authoritative SDK's locked environment. All paths below are
temporary and variable-driven; do not add Makefile defaults or generated SDK files to this
repository.

1. Copy this template to a temporary `exampleService` repository, resolve and sync its private
   dependency through GitHub SSH, import `pypokerlost`, and run `make check`, `make pre-commit`,
   the documentation checker, and the final diff check.
2. Add only in that temporary service:
   `EchoRequest(message: str)`, `EchoResponse(message: str)`, and public
   `POST /echo.sendMessage` with one `OPERATION = "echo.sendMessage"` constant. Publish success as
   `ApplicationResponse[EchoResponse]`, and publish 409/422/500 as
   `ApplicationResponse[None]`.
3. Add a temporary failure branch that returns a valid failed envelope with a non-2xx status. Do
   not change the published successful result schema.
4. Start the real FastAPI application/lifespan with valid required settings. PostgreSQL need not be
   contacted because the probe route is persistence-free.
5. Configure `OPENAPI_OPERATION=contract.getOpenAPI`, fetch `/contract.getOpenAPI`, and assert the
   envelope, OpenAPI 3.1.x, SemVer, exact service metadata,
   system paths, request component/body/no-parameters metadata, success envelope/result reference,
   and 409/422/500 error-envelope metadata.
6. From an ephemeral copy of the authoritative SDK source, using its locked toolchain, run service
   mode to one temporary output root:

   ```bash
   uv run python scripts/generate_methods.py service <base-url> \
     --openapi-operation contract.getOpenAPI \
     --output <service-output>
   ```

7. Save the actual wrapped publication's `result` (the raw OpenAPI document) to JSON and run file
   mode to a second temporary output root:

   ```bash
   uv run python scripts/generate_methods.py file <openapi.json> --output <file-output>
   ```

8. Compare generated Python sources byte-for-byte. Manifests are intentionally output-root scoped;
   compare their semantic generator/OpenAPI/source/service/files fields rather than paths.
9. Put the temporary generated output on the generated service's import path and use the installed
   `pypokerlost` dependency. Configure `APIServer.from_base(base_url)`, `HttpxSession`, and `Client`;
   call `await client(EchoMethod(message="hello"))`. Assert the exact generated `EchoResponse` type
   and `message == "hello"`.
10. Call the failure branch through the same generated method and assert `PokerlostAPIError` with
    only safe scalar `operation`, `status_code`, `error`, and `error_message` metadata. Do not print
    raw bodies or headers.
11. Run `ApplicationResponse` parity checks for fields/defaults/invariants, forbidden extras,
    frozen mutation, strict values, `hide_input_in_errors`, `validate_default`, model config, and
    representative JSON schema.
12. Run generator negatives for missing-dot, snake_case, multi-dot, uppercase-initial, hyphenated,
    and path-mismatched operation IDs; query/path parameters; free-form bodies; camelCase request
    fields; raw, wrong, or extended envelopes; incompatible 2xx schemas; and external `$ref`. Each
    case must fail before writing generated sources.
13. Terminate the server and remove temporary services, generated outputs, output-scoped manifests,
    captured OpenAPI, bytecode, and processes.

The pristine scaffold itself has only system paths, so fresh-copy verification does not require a
generator run. If invoked there, the generator reports
`OpenAPI document contains no non-system API operations`; that is expected and is why the temporary
operation is mandatory for the positive compatibility probe.

## Copier, image, and deployment regression

Every compatibility change also runs a fresh Copier copy and an update regression from a temporary
prior-template Git snapshot. Modify `SERVICE.md` before update and verify it remains byte-identical.
No new Copier question is needed for SDK compatibility, and PostgreSQL stays unconditional.

The generated Dockerfile uses Python 3.14 in builder and runtime stages. Builder-only `git` and
`openssh-client` resolve the pinned private dependency through a BuildKit SSH-agent mount and an
explicit trusted `known_hosts` input on every `uv sync`; only the installed virtual environment is
copied to runtime. Verify the runtime has no SSH material, agent socket, Git credential, `git`, or
`openssh-client`. Helm requires no SDK repository credentials; its root `GET /` probe remains
unchanged.

## Current SDK non-goals

The SDK currently provides typed HTTP method calls, middleware, immutable request headers, storage,
lifecycle, and method generation. It does not provide built-in auth/token refresh, authorization
middleware, retries, automatic service routing, WebSocket/events, streaming, or subscriptions.
The pristine template must not simulate those features or instantiate an unused SDK client.

## Update policy

Before changing Python version, operation/path rules, request serialization, response contracts,
OpenAPI publication, or SDK integration guidance:

1. inspect the current SDK working tree and its public facades;
2. record the inspected SDK commit/distribution/generator versions here;
3. reconcile implementation/documentation differences in favor of implementation and report them;
4. update the server-local contract without compatibility wrappers;
5. increase a service's `info.version` when canonical API content changes;
6. run the complete probe, negative matrix, Copier copy/update, and generated-service checks;
7. verify the SDK checkout remains byte-for-byte unmodified.

The template does not provide `sdk-generate` or `sdk-check` Makefile targets: normal service
commands must not assume a sibling checkout, and generator output/manifest ownership belongs to the
SDK repository. Use the explicit variable-driven commands above during compatibility work.
