# Changelog

All notable template changes are documented here. Releases use PEP 440-compatible Git tags.

## Unreleased

- Document the canonical target-specific `pypokerlost.Client` lifecycle, SDK client-credentials
  provider, outbound middleware order, explicit bounded per-call retry, business-idempotency and
  transaction boundaries, and Secret-only credential wiring while keeping pristine services free
  of target clients and outbound settings.
- Require settings-driven root and OpenAPI publication operations, register their routes at
  application composition, and enforce the exact two-segment lowerCamelCase operation contract.
- Generate the canonical keyed business-operation fingerprint primitive and optional typed key
  settings, including Helm Secret-reference and key-version configuration foundations.
- Replace relative inter-file Markdown links with repository-root references in backticks and make
  the documentation checker enforce that policy in template and generated repositories.
- Add disposable `template-copy` and `template-check` targets for reproducible structural,
  documentation, and compile verification of a fresh Copier render.
- Remove the repository-local disposable template verifier and its Make targets; maintainers now
  follow the documented Copier copy/update workflow directly when validating generated services.
- Replace the generated two-page manual with canonical API-service documentation, a universal
  documentation checker, file-hygiene pre-commit hooks, and self-documenting root/generated
  Makefile quality workflows.
- Expand generated Git hygiene rules and restrict Docker build contexts to the files consumed by
  the generated `Dockerfile`.
- Stop generating `.python-version`; Python 3.14 remains aligned through project, Ruff, mypy, and
  Docker configuration.
- Removed generic OAuth2/scope/OpenAPI authorization mechanics from the base template; concrete
  services own FastAPI security declarations.
- Install `pypokerlost` in every generated service from its verified private GitHub SSH source at
  an immutable revision, including BuildKit SSH forwarding for image builds.
- Align generated services with Python 3.14 and the current `pypokerlost` operation contract:
  exact operation/path identity, strict `ApplicationResponse` parity, SDK-compatible wrapped
  OpenAPI publication, generator/runtime compatibility verification, corrected SDK acronym casing,
  and generated SDK integration documentation.
- Use `service_name` as the only user-supplied service identity input.
- Make PostgreSQL, SQLAlchemy, and Alembic unconditional parts of the generated foundation.
- Separate shared generated conventions in `AGENTS.md` from the service-owned `SERVICE.md`.
- Use SQLAlchemy's async transaction context directly, normalize refused connections at the engine
  boundary, and map database failures by SQLAlchemy type.
- Add immutable domain value/category foundations and consistent application value bases.
- Define one generated artifact naming contract with narrow base and package exceptions.
- Add generated architecture documentation and separate document ownership.
- Align generated documentation with the wrapped snake_case API contract and Copier update flow.

No Copier migration exists in v1 because there is no older released generated layout to migrate.
