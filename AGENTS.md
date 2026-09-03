# serviceTemplate

This repository owns the shared Copier foundation for Pokerlost backend services.

## Before every task

1. Read this file, `TEMPLATE.md`, and `copier.yml`.
2. Read `SDK_COMPATIBILITY.md` before changing the operation contract,
   `PokerlostResponse`, header authorization, OpenAPI publication, Python support, or SDK integration.
3. Inspect the current template, documentation, Makefile, pre-commit configuration, and relevant
   generated source before editing.
4. Inspect the authoritative `pypokerlost` implementation whenever a shared SDK contract changes.
5. Preserve existing user changes and keep every change focused on the requested responsibility.

## Sources of truth

Use this priority order:

```text
latest direct user requirement
-> current pypokerlost implementation for SDK contracts
-> TEMPLATE.md and SDK_COMPATIBILITY.md
-> copier.yml and the current template tree
-> older repository history
```

The current checkout wins over stale prose. Do not add compatibility aliases for obsolete private
or pre-release layouts unless the user explicitly requires them.

## Repository boundary

- Keep this repository a Copier template, not a deployable business service or shared runtime
  package.
- Keep PostgreSQL, SQLAlchemy, Alembic, FastAPI, Docker, and Helm in the generated foundation.
- Keep generated services free of business/domain implementation, concrete persistence entities,
  credentials, authentication policy, and authorization policy.
- Keep `service_name` as the only user-supplied service identity unless generation genuinely needs
  another answer.
- Preserve generated `SERVICE.md` during Copier updates; it belongs to the generated service.
- Do not introduce sibling-path SDK dependencies, floating Git branches, embedded credentials, or
  alternative inter-service HTTP transports.

## Python, typing, and naming

- Target Python 3.14 for template-maintenance scripts and generated services.
- Begin project-owned Python modules with a focused module docstring followed immediately by
  `from __future__ import annotations`.
- Use a 100-character Python line length, strict mypy, built-in generics, `collections.abc`,
  `Self`, modern unions, explicit return types, and PEP 695 syntax where it expresses the contract.
- Use `snake_case` modules/functions/variables, `PascalCase` classes, and `UPPER_SNAKE_CASE`
  constants. Preserve canonical `API`, `HTTP`, `JSON`, `UUID`, `OpenAPI`, and `URL` acronym casing.
- Use Pokerlost consistently in prose and project-owned identifiers. Preserve the distribution
  name `pypokerlost`.
- Describe single lowerCamelCase operation names as API operations, method calls, or inter-service
  calls. Keep dotted lowerCamelCase scope names separate from operation IDs.

## Documentation

- Keep `README.md` concise and `docs/index.md` as the navigation hub.
- Write repository documentation in English with exactly one H1, a short opening paragraph,
  repository-root file references in backticks, and language-tagged code fences.
- Do not use relative inter-file Markdown links. Only `http://`, `https://`, `mailto:`, and
  same-document `#anchor` link destinations are allowed.
- Use `bash`, `python`, `toml`, `yaml`, `json`, `text`, `cpp`, or `cmake` fences as appropriate.
- Do not record prompts, chat notes, temporary plans, absolute local checkout paths, stale commands,
  invented verification, or unsupported guarantees.
- Update template-maintainer documentation and generated-service documentation together whenever a
  shared contract changes.

## Verification

- Use the root `Makefile` as the canonical command interface.
- Run `make format`, then `make check` and `make pre-commit` before handoff.
- After Copier structure changes, render into a disposable destination and run the generated
  service's documented checks when its private SDK dependency is available.
- When template-managed files change, verify a Copier update from a prior template revision and
  confirm service-owned `SERVICE.md` remains unchanged.
- Run the manual compatibility verification in `SDK_COMPATIBILITY.md` after changes to API operations,
  request/response envelopes, header authorization, OpenAPI, Python, or the SDK boundary.
- Report every unavailable tool, failed command, and external-service limitation.
- Do not add or modify tests unless the user explicitly requests them. Do not add rendered-template
  checkers, `scripts/check_*.py`, architecture checker scripts, or hidden equivalents.

## Git hygiene

- Inspect status, tracked and staged diffs, branch, remotes, and recent history before editing.
- Do not commit IDE metadata, caches, virtual environments, build output, credentials, `.env`, or
  disposable verification artifacts.
- Review `git diff --check` and the complete final diff before committing.
- Never use destructive Git commands or force push. Push only when the user explicitly requests it.
