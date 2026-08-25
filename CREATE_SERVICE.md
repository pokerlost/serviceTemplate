# Create and Update a PokerLost Service

This document is the Copier copy, update, and verification workflow. The generated-content
contract is defined in [`TEMPLATE.md`](TEMPLATE.md).

## Fresh copy

1. Read `AGENTS.md`, `TEMPLATE.md`, `copier.yml`, and this file.
2. Inspect the source checkout and resolve the destination requested by the user. Do not overwrite
   an unrelated project or create a nested `serviceTemplate/serviceTemplate` layout.
3. Resolve the only answer, `service_name`. It must be a non-empty ASCII camelCase or PascalCase
   name beginning with a letter and containing only letters and digits.
4. Run pinned Copier without `--trust`:

```bash
uvx --from 'copier==9.17.2' copier copy <template-source> <destination> \
  -d service_name=<SERVICE_NAME>
```

5. Inspect Copier-owned `.copier-answers.yml`; do not write or edit it manually.
6. Read the generated `AGENTS.md`, `SERVICE.md`, and `README.md`. Replace `SERVICE.md` `TODO`
   sections only with authoritative service facts.

## Fresh-copy verification

Confirm that the generated root contains `AGENTS.md`, `SERVICE.md`, `README.md`,
`docs/ARCHITECTURE.md`, `.copier-answers.yml`, `app/`, `alembic/`, and `deploy/helm/`. Then run:

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

Verify the generated imports and artifact naming structurally. Exercise `GET /` and
`GET /openapi.get`, confirm both return `ApplicationResponse`, confirm
`x-pokerlost-service.id`, and confirm `/openapi.json`, `/docs`, and `/redoc` are disabled.

When the environment permits, use an ephemeral route or dependency probe against an unavailable
PostgreSQL address to confirm `OperationalError` becomes a safe HTTP 503 response. Use a temporary
PostgreSQL instance to probe commit on normal dependency exit and rollback on exceptional exit.
Never retain probe routes, tables, schemas, or migrations in the generated service.

## Template update

Run updates from a clean generated service checkout with valid Copier answers metadata:

```bash
uvx --from 'copier==9.17.2' copier check-update
uvx --from 'copier==9.17.2' copier update
```

Review the complete diff and repeat the fresh-copy checks. For a template change that manages
generated files, the update regression must also:

1. create a fresh service from the prior template revision;
2. modify its service-owned `SERVICE.md`;
3. update from a revision containing a safe template-owned change;
4. confirm the template-owned file and any new files update;
5. confirm `SERVICE.md` remains byte-for-byte unchanged;
6. confirm `.copier-answers.yml` remains valid Copier metadata.

Report every unavailable tool, failed command, and external-service limitation. Do not claim a
check that was not executed.
