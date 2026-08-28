# serviceTemplate ↔ pypokerlost compatibility

This is the canonical maintainer contract and verification procedure for the generated server
template. Service-author guidance belongs in generated `docs/api/rpc-contract.md`,
`docs/api/application-response.md`, and `docs/api/openapi-and-sdk.md`; short normative constraints
belong in generated `AGENTS.md`.

## Authoritative checkout inspected

The compatibility work on 2026-08-28 inspected the following `main` revision of the private
[`pokerlost/pypokerlost`](https://github.com/pokerlost/pypokerlost):

```text
remote:               git@github.com:pokerlost/pypokerlost.git
distribution version: 0.1.0
commit:               4d375903c2002bd9f09a59a876b7cf7ea8b7470b
remote main verified: 43d457ec088371211af1c94b32b747adce57005e
matching release tag: none
generator version:    0.2.1
Python:               >=3.13
```

The SDK working tree is a read-only authoritative source. Its implementation wins over SDK prose
when they differ. Re-inspect the current working tree rather than assuming this recorded commit is
still current.

The SDK and template remotes have the same GitHub owner, `pokerlost`. At final verification, remote
`main` was one commit ahead of the inspected revision. That descendant changes only SDK
`.gitignore` and `.dockerignore`; the runtime package, generator, project metadata, and version are
unchanged. Neither local nor remote tags contain a release tag for version `0.1.0`. Generated
services remain pinned to the inspected, verified full commit SHA at
`ssh://git@github.com/pokerlost/pypokerlost.git`. Never substitute a sibling path, absolute path,
`file://` source, embedded credential, unverified index, or floating branch.

## Compatibility boundary

| Contract                 | SDK implementation                                    | Generated-service requirement                                                                       |
|--------------------------|-------------------------------------------------------|-----------------------------------------------------------------------------------------------------|
| Python and style         | `pyproject.toml`                                      | Python >=3.13, Ruff `py313`, mypy 3.13, line length 100, Python 3.13 images                         |
| SDK installation         | distribution `pypokerlost`                           | verified private SSH source pinned to one immutable release tag or full commit SHA                  |
| RPC operation            | `pypokerlost/types/rpc.py`                            | `^[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)+$`                                                           |
| HTTP method              | `pypokerlost/types/rpc.py`                            | only GET, POST, PUT, PATCH, DELETE; POST default                                                    |
| Runtime URL              | `environment/api_server.py`                           | one API base plus `/<operation>`                                                                    |
| Generator path           | `scripts/generate_methods.py`                         | path is exactly `"/" + operationId`                                                                 |
| Request serialization    | `request/rpc_request_builder.py`                      | alias-free snake_case fields matching `model_dump(mode="json", by_alias=False, exclude_unset=True)` |
| Request body             | `scripts/generate_methods.py`                         | one named typed JSON object, or no body for a parameterless OpenAPI operation; no parameters        |
| Response base            | `contracts/response_model.py`                         | exact strict immutable local `ResponseModel` config                                                 |
| Wire envelope            | `contracts/application_response.py`                   | exact four fields/defaults/invariants; no extensions                                                |
| Response decoding        | `response/application_response_handler.py`            | failed envelope/API error, success+non-2xx/protocol error, invalid JSON/decode error                |
| Publication endpoint     | `scripts/generate_methods.py`                         | wrapped `GET /openapi.get`, operation ID `openapi.get`                                              |
| System paths             | `scripts/generate_methods.py`                         | exactly `/` and `/openapi.get`; no generated methods                                                |
| OpenAPI document         | `scripts/generate_methods.py`                         | OpenAPI 3.1.x and SemVer `info.version`                                                             |
| Service metadata         | `scripts/generate_methods.py`                         | exactly `x-pokerlost-service: {id: SERVICE_NAME}`                                                   |
| Generator subset         | `scripts/generate_methods.py`                         | only the supported reachable schema subset; focused failure otherwise                               |
| Runtime target/lifecycle | `client/client.py`, `client/session/httpx_session.py` | one explicit APIServer per session/client, lifespan ownership, deterministic close                  |

Service identity and RPC identity are separate. `x-pokerlost-service.id` retains the Copier
`service_name`, including possible uppercase letters. Business operation IDs never derive directly
from it. The root system operation uses the lowercase `service_slug` namespace.

## Server contract

Canonical business RPC:

```text
operation = lowercase namespace.method
path      = /<same operation>
request   = named closed typed JSON body, absent only when parameterless
success   = ApplicationResponse[<SemanticName>Response]
errors    = ApplicationResponse[None]
```

Each route module declares one `OPERATION` constant and derives both decorator values from it.
Application-owned JSON is alias-free `snake_case`. A request schema is `<SemanticName>Request`, a
result schema is `<SemanticName>Response`, and typed nested objects are named closed components.
OpenAPI parameters and `Body(embed=True)` are not part of PokerLost RPC transport. A `GET` with
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
   `EchoRequest(message: str)`, `EchoResponse(message: str)`, and public `POST /echo.send` with one
   `OPERATION = "echo.send"` constant. Publish success as
   `ApplicationResponse[EchoResponse]`, and publish 409/422/500 as
   `ApplicationResponse[None]`.
3. Add a temporary failure branch that returns a valid failed envelope with a non-2xx status. Do
   not change the published successful result schema.
4. Start the real FastAPI application/lifespan with valid required settings. PostgreSQL need not be
   contacted because the probe route is persistence-free.
5. Fetch `/openapi.get` and assert the envelope, OpenAPI 3.1.x, SemVer, exact service metadata,
   system paths, request component/body/no-parameters metadata, success envelope/result reference,
   and 409/422/500 error-envelope metadata.
6. From an ephemeral copy of the authoritative SDK source, using its locked toolchain, run service
   mode to one temporary output root:

   ```bash
   uv run python scripts/generate_methods.py service <base-url> --output <service-output>
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
12. Run generator negatives for camelCase/no-dot operation IDs, path mismatch, query/path
    parameters, free-form body, camelCase request field, raw/wrong/extended envelope, incompatible
    2xx schemas, and external `$ref`. Each case must fail before writing generated sources.
13. Terminate the server and remove temporary services, generated outputs, output-scoped manifests,
    captured OpenAPI, bytecode, and processes.

The pristine scaffold itself has only system paths, so fresh-copy verification does not require a
generator run. If invoked there, the generator reports
`OpenAPI document contains no non-system RPC operations`; that is expected and is why the temporary
RPC is mandatory for the positive compatibility probe.

## Copier, image, and deployment regression

Every compatibility change also runs a fresh Copier copy and an update regression from a temporary
prior-template Git snapshot. Modify `SERVICE.md` before update and verify it remains byte-identical.
No new Copier question is needed for SDK compatibility, and PostgreSQL stays unconditional.

The generated Dockerfile uses Python 3.13 in builder and runtime stages. Builder-only `git` and
`openssh-client` resolve the pinned private dependency through a BuildKit SSH-agent mount and an
explicit trusted `known_hosts` input on every `uv sync`; only the installed virtual environment is
copied to runtime. Verify the runtime has no SSH material, agent socket, Git credential, `git`, or
`openssh-client`. Helm requires no SDK repository credentials; its root `GET /` probe remains
unchanged.

## Current SDK non-goals

The SDK currently provides typed HTTP RPC, middleware, immutable request headers, storage,
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

## Known SDK prose differences at the inspected revision

- The example envelope in `docs/generating_methods.md` marks all four fields required, while the
  implementation requires only `ok`; the template follows implementation defaults.
- `docs/adding_methods.md` demonstrates a manually authored `*Result`; generated referenced server
  components preserve their `*Response` names, which is the template convention.
- SDK service-mode discovery calls `raise_for_status()` before parsing the publication envelope, so
  a non-2xx `/openapi.get` is a fetch failure even if its body is a valid failed envelope. Normal
  successful publication is HTTP 200.
