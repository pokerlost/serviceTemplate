# Create a PokerLost Service with Copier

This workflow is for Codex or another agent creating a service from this template. Use Copier
directly; do not manually copy the tree or create a second generator.

## 1. Read the template contract

Read, in order:

1. `AGENTS.md`;
2. `TEMPLATE.md`;
3. `copier.yml`;
4. this file.

Inspect the source checkout before choosing a destination.

## 2. Resolve the only answer

The only required answer is the canonical service identity:

```text
service_name
```

It must be a non-empty ASCII camelCase or PascalCase name that starts with a letter and contains
letters and digits only, for example `authService`, `virtualMoney`, or `PokerServer`.

Do not ask architecture questionnaires during mechanical generation. In particular, the template
does not ask:

```text
service_role
service_purpose
out_of_scope
data_ownership
secondary_storage
external_dependencies
special_invariants
auth_policy
realtime_policy
first_production_scope
primary_storage
use_postgresql
```

Copier derives the slug, environment prefix, and database name. PostgreSQL is always included.

## 3. Choose the destination

Use the destination explicitly named by the user. If it is implicit, derive the intended service
directory from the current workspace and `service_name`, then confirm that it does not overwrite
an unrelated project.

The destination must not be a nested copy such as `target/serviceTemplate` or
`serviceTemplate/serviceTemplate`. Do not create a nested `.git` or a repository beside the
requested destination.

## 4. Generate with Copier 9.17.2

Run the pinned tool without `--trust`:

```bash
uvx --from 'copier==9.17.2' copier copy <template-source> <destination> \
  -d service_name=<SERVICE_NAME>
```

The template has no tasks or hooks requiring trusted execution.

## 5. Verify the generated repository

Confirm that the generated root contains `AGENTS.md`, `SERVICE.md`, `README.md`,
`.copier-answers.yml`, the Python project files, `app/`, `alembic/`, and `deploy/helm/`. Inspect
`.copier-answers.yml` as Copier output; never hand-write or manually edit it.

Initialize and verify the locked environment using the generated repository's documented flow:

```bash
cd <destination>
uv lock
uv lock --check
make format
make lint
make typecheck
make pre-commit
python -m compileall -q app alembic/env.py
git diff --check
```

Also verify that `GET /` and `GET /openapi.get` return `ApplicationResponse`, built-in FastAPI
OpenAPI/docs URLs are disabled, PostgreSQL/Alembic files exist, and no business implementation was
generated.

## 6. Read the generated contract

Before adding service code, read the generated `AGENTS.md` and `SERVICE.md`. They now govern work
inside that service.

Replace `TODO` sections in `SERVICE.md` only with concrete facts known from the user's request or
authoritative project context. Never invent responsibilities, data ownership, boundaries, or
invariants merely to make the document look complete. Leave unknown facts as `TODO`.

## 7. Check and apply template updates

Run update commands from a clean generated service checkout that contains its Copier answers file:

```bash
uvx --from 'copier==9.17.2' copier check-update
uvx --from 'copier==9.17.2' copier update
```

Then review the complete diff and repeat the generated-service verification. Confirm specifically
that template-owned files changed as expected, `.copier-answers.yml` remains valid Copier metadata,
and the service-owned `SERVICE.md` was not overwritten.
