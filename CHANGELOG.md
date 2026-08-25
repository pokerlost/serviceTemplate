# Changelog

All notable template changes are documented here. Releases use PEP 440-compatible Git tags.

## Unreleased

- Use `service_name` as the only user-supplied service identity input.
- Make PostgreSQL, SQLAlchemy, and Alembic unconditional parts of the generated foundation.
- Separate shared generated conventions in `AGENTS.md` from the service-owned `SERVICE.md`.
- Add minimal non-Pydantic application command, query, result, and handler bases.
- Align generated documentation with the wrapped snake_case API contract and Copier update flow.

No Copier migration exists in v1 because there is no older released generated layout to migrate.
