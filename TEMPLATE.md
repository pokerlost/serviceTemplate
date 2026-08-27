# PokerLost Service Template

## Purpose

`serviceTemplate` is the reusable Copier baseline for PokerLost backend services. It generates
infrastructure and general architectural primitives, never a concrete service domain. Its HTTP
wire contract and OpenAPI 3.1 publication are compatible with the authoritative `pypokerlost` SDK
described in [`SDK_COMPATIBILITY.md`](SDK_COMPATIBILITY.md).

## Generation contract

Copier 9.17.2 asks for one canonical camelCase or PascalCase identity:

```text
service_name
```

It derives `service_slug`, `service_env_prefix`, and `database_name`. PostgreSQL is an
unconditional part of every generated service; there are no architecture questionnaires or
optional primary-storage branches.

Generated services require Python 3.13 or newer. The Python, Ruff, mypy, builder-image, and
runtime-image versions move together; generated source uses a 100-character line length.

## Generated foundation

Every generated service includes:

```text
FastAPI
Pydantic v2 and Pydantic Settings
PostgreSQL, SQLAlchemy 2, and Alembic
Logfire instrumentation foundations
Gunicorn with Uvicorn workers and a Typer CLI
Docker and Helm deployment foundations
uv, Ruff, mypy, and pre-commit
```

The source tree separates `api`, `application`, `domain`, `configuration`, `observability`,
`persistence`, and `cli`. The domain foundation contains the immutable internal `ValueModel` base
at `domain/value_model.py` and the deployment `Environment` category at
`domain/enums/environment.py`. The application layer builds its `Command`, `Query`, and `Result`
value bases on `ValueModel` and provides an abstract asynchronous `Handler` contract.

Persistence provides reusable SQLAlchemy metadata, repository, result-reader, and projection
foundations without a concrete model, table, or migration. One request-owned session and
transaction is opened with SQLAlchemy's async context manager: normal exit commits, exceptional
exit rolls back, and context exit closes the session. SQLAlchemy errors are mapped centrally at
the API boundary: `OperationalError` is an availability failure and other `SQLAlchemyError`
instances are sanitized internal failures. Both use `ApplicationResponse`: availability maps to
HTTP 503 and other SQLAlchemy failures map to HTTP 500. The engine boundary narrowly normalizes an
exact driver-level `ConnectionRefusedError` into `OperationalError`; the request dependency does
not translate exceptions.

## Public API contract

- `GET /` and `GET /openapi.get` are the two SDK system paths.
- A business RPC operation is a lowercase `namespace.method`, and its path is exactly the same
  value prefixed with `/`.
- Business inputs use one named, closed, typed JSON request body; RPC transport does not use OpenAPI
  path, query, header, or cookie parameters.
- Every success uses `ApplicationResponse[ResponseType]`; handled errors use
  `ApplicationResponse[None]`.
- Application-owned JSON uses `snake_case`.
- FastAPI generates OpenAPI 3.1 with only the required `x-pokerlost-service.id` platform metadata.
- Built-in `/openapi.json`, `/docs`, and `/redoc` are disabled; `GET /openapi.get` publishes the
  wrapped document.
- Public dependencies use PEP 695 aliases with private resolver functions.

The complete artifact naming contract, including API, ORM, projection, base-class, operation
package, and enum conventions, lives only in the generated `AGENTS.md`.

## Generated documentation

- `AGENTS.md` is the normative shared PokerLost engineering rulebook.
- `SERVICE.md` is the service-owned record of concrete purpose, responsibilities, and local rules;
  Copier preserves it during updates.
- `README.md` is the operator and developer quickstart.
- `docs/ARCHITECTURE.md` explains the generated layers and request flow.
- `docs/SDK.md` owns practical RPC, OpenAPI, generator, and inter-service SDK rules.

## Intentionally absent

The template contains no business entities, business categories, authorization implementation,
tokens, credentials, ledger, poker or blockchain behavior, concrete persistence entity, fake
migration, OpenAPI registry, generated tests, or CI/CD. A generated service adds only the behavior
supported by its known `SERVICE.md` responsibilities.

## Ownership

Copier owns and evolves the reusable scaffold. After initial generation, the service owns
`SERVICE.md` and its explicitly requested business implementation. The release history of this
template is recorded in `CHANGELOG.md`; the copy and update procedure lives in
`CREATE_SERVICE.md`.
