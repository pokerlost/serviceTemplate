# PokerLost serviceTemplate

`serviceTemplate` is the shared Copier template for PokerLost backend services. It generates a
business-free FastAPI foundation with PostgreSQL, SQLAlchemy, Alembic, Logfire, Docker, Helm, and
the standard Python tooling used by the platform. Generated services publish the strict PokerLost
RPC/OpenAPI wire contract and install the verified `pypokerlost` SDK from a pinned private GitHub
SSH source.

The template supports Copier 9.17.2 and asks only for `service_name`.
Generating and locking a service requires GitHub SSH read access to `pokerlost/pypokerlost`; no
repository credential is stored in the template.

## Generate a service

```console
uvx --from 'copier==9.17.2' copier copy /path/to/serviceTemplate /path/to/service \
  -d service_name=exampleService
```

Trusted execution is not required. After generation, follow the generated `README.md` and read its
`AGENTS.md` and `SERVICE.md` before adding service behavior.

## Documentation

- [`TEMPLATE.md`](TEMPLATE.md) is the canonical contract for generated content and omissions.
- [`CREATE_SERVICE.md`](CREATE_SERVICE.md) contains the Copier copy, update, and verification
  workflow.
- [`SDK_COMPATIBILITY.md`](SDK_COMPATIBILITY.md) is the authoritative template-maintainer contract
  and end-to-end SDK compatibility procedure.

## Maintain the template

The root Makefile is a thin interface for documentation, pre-commit, and disposable Copier checks:

```console
make help
make check
make check-full
```

`make check-full` resolves the pinned private SDK in a temporary generated service and therefore
requires `uv`, network access, and an SSH agent identity authorized for `pokerlost/pypokerlost`.
