# PokerLost serviceTemplate

`serviceTemplate` is the shared Copier template for PokerLost backend services. It generates a
business-free FastAPI foundation with PostgreSQL, SQLAlchemy, Alembic, Logfire, Docker, Helm, and
the standard Python tooling used by the platform.

The template supports Copier 9.17.2 and asks only for `service_name`.

## Generate a service

```bash
uvx --from 'copier==9.17.2' copier copy /path/to/serviceTemplate /path/to/service \
  -d service_name=exampleService
```

Trusted execution is not required. After generation, follow the generated `README.md` and read its
`AGENTS.md` and `SERVICE.md` before adding service behavior.

## Documentation

- [`TEMPLATE.md`](TEMPLATE.md) is the canonical contract for generated content and omissions.
- [`CREATE_SERVICE.md`](CREATE_SERVICE.md) contains the Copier copy, update, and verification
  workflow.
