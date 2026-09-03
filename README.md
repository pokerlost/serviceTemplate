# Pokerlost serviceTemplate

`serviceTemplate` is the shared Copier template for Pokerlost backend services. It generates a
business-free FastAPI foundation with PostgreSQL, SQLAlchemy, Alembic, Logfire, Docker, Helm, and
the standard Python tooling used by the platform. Services with protected operations publish
standard OAuth2 client-credentials scope metadata, accept bearer access tokens through the
Authorization header, and install the verified `pypokerlost` SDK from a pinned private GitHub SSH
source. Public-only services do not publish an unused scheme.

Generated documentation separates SDK-owned transport/middleware from the service-owned local token
verifier and business behavior. The pristine runtime provides canonical request/response envelopes,
an empty exact-scope catalog, and a fail-closed verifier seam without a fake verifier, outbound
client, credentials, token store, refresher, or retry configuration.

The template supports Copier 9.17.2, asks only for `service_name`, and requires Python 3.14 or newer
for repository maintenance and generated services.
Generating and locking a service requires GitHub SSH read access to `pokerlost/pypokerlost`; no
repository credential is stored in the template.

## Generate a service

```bash
uvx --from 'copier==9.17.2' copier copy <template-source> <destination> \
  -d service_name=exampleService
```

Trusted execution is not required. After generation, follow the generated `README.md` and read its
`AGENTS.md` and `SERVICE.md` before adding service behavior.

## Documentation

- `docs/index.md` is the repository documentation home.
- `TEMPLATE.md` is the canonical contract for generated content and omissions.
- `CREATE_SERVICE.md` contains the Copier copy, update, and verification
  workflow.
- `SDK_COMPATIBILITY.md` is the authoritative template-maintainer contract
  and end-to-end SDK compatibility procedure.

## Maintain the template

The root Makefile is a thin interface for documentation and pre-commit checks:

```bash
make help
make check
make check-full
```

The tooling-only `pyproject.toml` records the Python, Ruff, mypy, and pre-commit baseline. Root
commands resolve those pinned tools with `uvx`; generated services instead use their locked
project environment.

Render one disposable Copier service manually when template structure changes, inspect it, and
remove it after verification. No rendered-template checker or permanent test is part of the
template-maintenance gate unless a task explicitly requests one. Follow `CREATE_SERVICE.md` for
dependency-backed generated-service and SDK verification.
