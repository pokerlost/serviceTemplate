# Changelog

All notable template changes are documented here. Releases use PEP 440-compatible Git tags.

## Unreleased

- Align generated services with Python 3.13 and the current `pypokerlost` RPC contract: exact
  operation/path identity, strict `ApplicationResponse` parity, SDK-compatible wrapped OpenAPI
  publication, generator/runtime compatibility verification, corrected SDK acronym casing, and
  generated SDK integration documentation.
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
