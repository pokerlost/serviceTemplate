# serviceTemplate ↔ pypokerlost compatibility

This is the canonical maintainer contract and verification procedure for the generated server
template. Service-author guidance belongs in generated API and architecture documentation; short
normative constraints belong in generated `AGENTS.md`.

## Authoritative SDK revision

The generated dependency uses the published and verified unified foundation SDK revision:

```text
remote:               git@github.com:pokerlost/pypokerlost.git
distribution version: 0.2.0
current dependency:   f2de9e11e66c52685d7324b0d70d747358a8d6e1
foundation pin:       f2de9e11e66c52685d7324b0d70d747358a8d6e1
Python:               >=3.14
```

Replace the dependency revision in `template/pyproject.toml.jinja`, this section, and the rendered
contract verifier only with the exact full SDK SHA confirmed on `origin/main`. Then lock every
generated service against that same revision. Never use a sibling path, absolute path, `file://`
source, embedded credential, unverified index, or floating branch.

## Compatibility boundary

| Contract | Canonical owner | Generated-service requirement |
| --- | --- | --- |
| Python and style | SDK and template project metadata | Python >=3.14, Ruff `py314`, mypy 3.14, line length 100 |
| SDK installation | `pypokerlost` distribution | Private SSH source pinned to one full pushed SHA |
| API operation | `pypokerlost.types.APIOperation` | Exactly `namespace.someOperation` |
| OAuth scope | `pypokerlost.types.OAuthScope` | At least two dot-separated lowerCamelCase segments |
| Shared authorization data | `pypokerlost.contracts.authorization` | Reuse canonical models and enums; no local wire copies |
| Runtime target | `pypokerlost.client.api_server.APIServer` | One explicit target per concrete client |
| Request objects | `pypokerlost.client.request` | Generic immutable headers and standard body content |
| Retry | `pypokerlost.client.retry.PokerLostRetryPolicy` | Fixed explicit per-call opt-in only |
| Wire envelope | SDK decoder and local `ApplicationResponse` | Exact four fields/defaults/invariants |
| OpenAPI publication | FastAPI and generated template | Standard OpenAPI plus `x-pokerlost-service.id` |
| Generated methods | SDK generator | Standard paths, request bodies, responses, security, and schemas |
| Token lifecycle | Consuming service | Application port, SDK adapter, optional service-owned storage |
| Business idempotency | Consuming service/template primitive | Same operation key, semantic payload, and target operation |

The target public imports are:

```python
from pypokerlost import Client, PokerlostMethod, Response
from pypokerlost.client.api_server import APIServer
from pypokerlost.client.request import Request, RequestBuilder, RequestOptions
from pypokerlost.client.response import ResponseHandler
from pypokerlost.client.retry import PokerLostRetryPolicy
from pypokerlost.contracts.authorization import (
    AccessTokenClaims,
    AuthorizationContext,
    AuthorizationRole,
    OAuthTokenResponse,
    OAuthTokenType,
    PrincipalStatus,
    PrincipalType,
)
from pypokerlost.types import APIOperation, HTTPMethod, OAuthScope
```

Generated method and response imports remain in their service-specific SDK packages. Service
identity and operation identity are separate: `x-pokerlost-service.id` retains the Copier
`service_name`, while API operation segments begin with lowercase ASCII letters.

## SDK boundary

The SDK owns:

```text
HTTP transport and target description
request construction and serialization
generic immutable per-call headers
ApplicationResponse decoding
canonical transport exceptions
generated methods and request/response types
shared authorization wire/value contracts
canonical transport retry execution
```

The SDK does not acquire, store, cache, refresh, invalidate, sign, verify, or revoke tokens. It does
not own client credentials or secrets, choose scopes or audience, inject bearer credentials through
auth-specific middleware, start background token tasks, or replay an operation after `401`.

When a consuming service needs a token, dependency direction is:

```text
application use case
-> service-owned application port
-> service-owned pypokerlost adapter
-> generated oauth.token method
-> optional service-owned token store
```

The pristine template creates none of these target-specific objects.

## Server contract

Canonical business operation:

```text
operation = namespace.someOperation
path      = /<same operation>
success   = ApplicationResponse[<SemanticName>Response]
errors    = ApplicationResponse[None]
```

The operation pattern is:

```text
^[a-z][A-Za-z0-9]*\.[a-z][A-Za-z0-9]*$
```

`GET /` is the sole path exception. Root and OpenAPI publication operations come from validated
settings. Router factories create an `APIRouter`, declare closure endpoints with decorators, and
return it. Stable business operation strings appear directly in decorator arguments. Imperative
route registration, mutable module-level routers, route-level operation constants, and post-hoc
route mutation are incompatible.

Application-owned JSON uses alias-free `snake_case`. Ordinary business inputs use one named,
closed, typed JSON body. Standard endpoint-specific media types remain available when the target
contract requires them.

`POST /oauth.token` has this exact contract:

```text
path:            /oauth.token
operation_id:    oauth.token
request media:   application/x-www-form-urlencoded
success:         ApplicationResponse[OAuthTokenResponse]
failure:         ApplicationResponse[None]
```

The generated method obtains operation, path, content type, request model, and response result model
from standard OpenAPI. Confidential-client authentication is supplied by the consuming adapter
through generic request headers. The SDK has no token-specific transport routine.

The local `ResponseModel` configuration remains:

```python
ConfigDict(
    extra="forbid",
    frozen=True,
    hide_input_in_errors=True,
    strict=True,
    validate_default=True,
)
```

`ApplicationResponse` has exactly `ok`, `result`, `error`, and `error_message`. Success forbids
error metadata. Failure requires both error fields and forbids a result. The schema has exactly
four properties and `additionalProperties: false`.

## OAuth scope and shared authorization contracts

`OAuthScope` accepts at least two dot-separated segments matching:

```text
^[a-z][A-Za-z0-9]*(\.[a-z][A-Za-z0-9]*)+$
```

The standard scope string parser rejects duplicates and empty tokens; its formatter sorts scopes
lexicographically. API operations use exactly two segments, while scopes may use more, so these
types are not interchangeable.

`OAuthTokenResponse`, `AccessTokenClaims`, `AuthorizationContext`, and the cross-service enums are
strict immutable data contracts. They contain validation and deterministic conversion only, never
network, token lifecycle, signing, verification, role expansion, or authorization decisions.
Token-bearing fields are hidden from representations and validation errors.

When an OpenAPI component is one of these canonical shared schemas, the generator reuses the SDK
model through one exact built-in mapping. It validates schema compatibility and fails closed on a
same-named incompatible component. It does not use runtime reflection, plugin registration, Python
import extensions, or route extra metadata.

## Standard OpenAPI

FastAPI generates and caches OpenAPI 3.1. The template adds only:

```yaml
x-pokerlost-service:
  id: <SERVICE_NAME>
```

The generator derives its contract from standard paths, `operationId`, request-body content,
responses, schemas, security schemes, and operation security. Route-level project extensions and
custom authorization metadata are forbidden. FastAPI security dependencies own concrete OAuth2
security declarations and exact scopes.

Supported request bodies include the established named JSON object and standard form content used
by actual schemas. Content-type support is generic rather than keyed to an operation name.

## Generic headers

Per-call headers are an immutable transport capability. Header names receive case-insensitive
duplicate protection, values reject CR/LF injection, caller mappings cannot mutate shared state,
and merging is deterministic. `Authorization`, `Cookie`, and `Proxy-Authorization` values are
redacted from representations, logs, telemetry, and errors.

Services do not add auth-specific SDK middleware solely to set a header.

## Canonical retry

Retry remains disabled when `RequestOptions.retry` is `None`. Every service opts in through:

```python
RequestOptions(
    retry=PokerLostRetryPolicy(),
)
```

The immutable first policy has no service configuration arguments:

```text
max_attempts = 3, including the first attempt
initial_delay_seconds = 0.2
max_delay_seconds = 2.0
backoff_multiplier = 2.0
jitter = full
retryable_status_codes = 408, 425, 429, 500, 502, 503, 504
respect Retry-After = true
total logical-call budget = 5.0 seconds
```

It retries canonical connection and timeout errors and listed statuses. A retryable proxy status
with an empty or malformed body may retry before final decoding. It does not retry `401`, `403`,
`404`, `409`, `410`, `422`, local validation or serialization errors, non-retryable application
failures, caller cancellation, or decode/protocol failures without a retryable status.

Backoff uses full jitter. Valid delta-seconds and HTTP-date `Retry-After` values are honored only
within the remaining fixed budget. Exhaustion preserves the normal final canonical SDK exception.
Services do not define retry attempt, delay, multiplier, status, or budget settings.

Transport retry does not prove semantic replay safety. A mutation may opt in only when every
attempt reuses the same `business_operation_id`, semantic payload, and target operation.

## Mandatory compatibility probe

Use actual Copier 9.17.2, a disposable generated service, and the authoritative SDK locked
environment:

1. Render an `exampleService`, resolve its pinned SDK dependency, and run generated checks.
2. Assert root and OpenAPI routers are closure factories using decorators and validated operation
   arguments.
3. Add a temporary decorated `POST /echo.sendMessage` JSON operation and publish success and
   handled error envelopes.
4. Publish the real wrapped OpenAPI document and generate SDK methods in service and file modes.
5. Compare generated Python sources byte-for-byte and manifests semantically.
6. Call the generated echo method through `Client` and assert typed success and canonical failure.
7. Add a temporary `POST /oauth.token` schema with standard form request content and
   `ApplicationResponse[OAuthTokenResponse]`.
8. Generate and call `OAuthTokenMethod`; assert generic form serialization, propagation of a
   caller-supplied safe test `Authorization` header, and shared response-model decoding.
9. Assert no preliminary token request, stored-token lookup, refresh, background task, or `401`
   replay occurs.
10. Assert canonical shared schemas are reused and same-named incompatible schemas fail generation.
11. Run operation negatives for missing-dot, snake_case, multi-dot, uppercase-initial, hyphenated,
    and path-mismatched IDs, and scope negatives for underscores, hyphens, empty segments,
    wildcard, whitespace, and uppercase initials.
12. Assert standard security schemes and operation scopes survive publication and generation
    without project-owned route metadata.
13. Remove all temporary routes, generated files, captured OpenAPI, bytecode, and processes.

Use disposable sessions or a local server to verify retry:

| Case | Expected attempts/result |
| --- | --- |
| No policy | One attempt |
| Connection error | At most three attempts |
| Malformed `503` | At most three attempts, then canonical final error |
| `429` with valid `Retry-After` | Honored only within budget |
| `401`, `409`, or `422` | One attempt |
| Caller cancellation | Immediate propagation |

Verify header duplicate rejection, CR/LF rejection, immutability, deterministic merge, and sensitive
redaction without printing a secret value.

## Copier and generated-service regression

Every compatibility change requires:

1. a fresh disposable copy;
2. an update from the exact prior template commit;
3. a byte-identical service-owned `SERVICE.md`;
4. preserved service migrations and business handlers;
5. removal of obsolete unchanged template-owned files;
6. one shared `application/ports/handler.py`;
7. the focused camelCase v2 `application/idempotency` package;
8. no local or path SDK dependency;
9. a fixed-point SDK generation check against final service OpenAPI.

The generated Dockerfile resolves the pinned private SDK through BuildKit SSH forwarding and an
explicit trusted `known_hosts` input. Runtime images and Helm configuration contain no SDK
repository credentials. Pristine settings, resources, environment examples, and Helm values
contain no target client, authService credentials, token storage, or retry algorithm settings.

## Update policy

Before changing operation/path rules, request serialization, shared response contracts, OpenAPI
publication, Python support, or SDK integration:

1. inspect the current SDK source and public facades;
2. reconcile implementation and documentation in favor of implementation;
3. update server and generator contracts without compatibility wrappers;
4. publish the SDK and pin its exact remote SHA;
5. run the complete compatibility, retry, header, shared-model, and Copier probes;
6. verify the SDK generator reaches a fixed point against final service OpenAPI;
7. report unavailable tools and external-service limitations.

The template does not provide generator Makefile targets or depend on a sibling SDK checkout.
Generator output and manifests belong to the SDK repository.
