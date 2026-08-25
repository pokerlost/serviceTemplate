# PokerLost serviceTemplate

This repository is the shared Copier template for PokerLost backend services. It generates a
domain-free FastAPI foundation with PostgreSQL, SQLAlchemy, Alembic, Logfire, Docker, Helm, and the
standard Python tooling used by the platform.

Read [`TEMPLATE.md`](TEMPLATE.md) for the generated architecture and
[`CREATE_SERVICE.md`](CREATE_SERVICE.md) for the agent workflow.

## Generate a service

The template supports Copier 9.17.2 and asks only for `service_name`. The slug, environment prefix,
and database name are computed automatically.

```bash
uvx --from 'copier==9.17.2' copier copy /path/to/serviceTemplate /path/to/service \
  -d service_name=exampleService
```

Trusted execution is not required. The template contains no Copier tasks or hooks.

The generated repository intentionally documents its lock initialization flow. Follow its README,
then read both generated governance files before adding service behavior:

```text
AGENTS.md
SERVICE.md
```

`SERVICE.md` begins with `TODO` sections. Fill them only with concrete, known service facts; do not
infer responsibilities from the service name.

## Ownership and updates

Copier owns the reusable scaffold. The generated service owns `SERVICE.md`, which is created on the
first copy and preserved by later template updates.

From a clean generated service checkout:

```bash
uvx --from 'copier==9.17.2' copier check-update
uvx --from 'copier==9.17.2' copier update
```

Review the full diff, rerun generated-project checks, and confirm that `SERVICE.md` remains
unchanged.

## Template verification

Template changes require both a fresh copy and, for template-owned file changes, an update smoke
scenario. The expected static and runtime checks are documented in `CREATE_SERVICE.md` and the
generated README. Report unavailable tools or external services rather than claiming an unexecuted
check.

Keep the scaffold free of concrete domain behavior and keep PostgreSQL unconditional.
