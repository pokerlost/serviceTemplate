# PokerLost serviceTemplate

`serviceTemplate` is the shared Copier template for PokerLost backend services. It generates a
business-free FastAPI foundation with PostgreSQL, SQLAlchemy, Alembic, Logfire, Docker, Helm, and
the standard Python tooling used by the platform. Generated services publish the strict PokerLost
API/OpenAPI operation contract and install the verified `pypokerlost` SDK from a pinned private
GitHub SSH source.

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

- [`docs/index.md`](docs/index.md) is the repository documentation home.
- [`TEMPLATE.md`](TEMPLATE.md) is the canonical contract for generated content and omissions.
- [`CREATE_SERVICE.md`](CREATE_SERVICE.md) contains the Copier copy, update, and verification
  workflow.
- [`SDK_COMPATIBILITY.md`](SDK_COMPATIBILITY.md) is the authoritative template-maintainer contract
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

`make check-full` adds the complete pre-commit hook pass to the regular non-mutating checks. Follow
[`CREATE_SERVICE.md`](CREATE_SERVICE.md) to verify a disposable generated service and its pinned
private SDK dependency.
