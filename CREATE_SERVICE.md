# Create and Update a PokerLost Service

This document is the Copier copy, update, and verification workflow. The generated-content
contract is defined in `TEMPLATE.md`.

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
7. Confirm the developer's normal GitHub SSH identity can read the private `pypokerlost`
   repository. Do not place a private key in the generated repository or `.env`.

## Fresh-copy verification

Confirm that the generated root contains `AGENTS.md`, `SERVICE.md`, `README.md`, `docs/index.md`,
the complete API-service documentation tree including
`docs/architecture/inter-service-clients.md`, `scripts/check_documentation.py`, `Makefile`,
`.pre-commit-config.yaml`, `.copier-answers.yml`, `app/`, `alembic/`, and `deploy/helm/`. Confirm
that every page under `docs/` is listed by its repository-root path in `docs/index.md`. Then run:

```bash
cd <destination>
cp .env.example .env
ssh-add -l
ssh -T git@github.com
uv lock
uv sync --locked
uv lock --check
uv run --locked python -c "import pypokerlost; print(pypokerlost.__version__)"
make help
make check
make pre-commit
make check-full
python -m compileall -q app alembic/env.py scripts
git diff --check
```

Verify the generated imports and artifact naming structurally. Exercise `GET /` and the configured
OpenAPI publication path through the real application lifespan and confirm:

- both endpoints return the exact four-field `ApplicationResponse` envelope;
- the wrapped document reports OpenAPI 3.1.x and a SemVer `info.version`;
- the top level contains exactly `x-pokerlost-service: {id: <service_name>}` for platform metadata;
- `.env.example` uses `/` with `<service_slug>.getRoot` and `/openapi.get` with `openapi.get`;
- replacing `ROOT_OPERATION` with `example.getRoot` changes only the root operation ID, while
  replacing `OPENAPI_OPERATION` with `contract.getOpenAPI` creates
  `/contract.getOpenAPI` with that same operation ID;
- `/openapi.json`, `/docs`, and `/redoc` are disabled;
- local `ResponseModel` and `ApplicationResponse` behavior matches the authoritative SDK contract.
- the canonical fingerprint module exists, has no static methods, and its deterministic probes
  cover order independence, changed values, framing, UTF-8, bytes, validation, and comparison.

Inspect `pyproject.toml` and `uv.lock`: `pypokerlost` must resolve from the configured private SSH
Git source at its immutable revision. Neither file may contain a sibling path, `file://` source,
embedded credential, password, token, or floating `main` branch.

Inspect the rendered `AGENTS.md` and inter-service client page for the target-specific lifecycle,
SDK service authentication, outer retry middleware, explicit per-call retry, business-idempotency,
transaction, and secret rules. Also confirm the pristine `ApplicationResources`, root `Settings`,
`.env.example`, and Helm chart contain no target client, outbound credentials, global retry policy,
or client registry.

When a Docker daemon is available, also verify the private dependency build and runtime package:

```bash
ssh-add -l
ssh-keygen -F github.com
docker build \
  --ssh default \
  --secret id=github_known_hosts,src="$HOME/.ssh/known_hosts" \
  -t pokerlost-sdk-template-probe:local \
  .
docker run --rm pokerlost-sdk-template-probe:local \
  python -c "import pypokerlost; print(pypokerlost.__version__)"
```

Inspect the runtime image to confirm it has no `/root/.ssh`, private keys, Git credentials, SSH
agent socket, `git`, or `openssh-client`, then remove the probe image. If `github.com` is absent
from `known_hosts`, configure a normal trusted GitHub SSH connection; never disable host
verification. Helm receives no GitHub build credential.

The pristine scaffold deliberately contains no non-system business operation, so fresh-copy
verification does not run or require SDK method generation. A generator success probe requires a
temporary business operation and must not leave that route in the service. After any operation
contract, envelope, OpenAPI publication, Python-version, or SDK integration change, run the
end-to-end procedure and negative matrix in `SDK_COMPATIBILITY.md`.

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
5. confirm `SERVICE.md` remains byte-for-byte unchanged, including when the new inter-service
   client page and `AGENTS.md` rules are rendered;
6. confirm obsolete unchanged template-owned pages are removed;
7. confirm `.copier-answers.yml` remains valid Copier metadata;
8. repeat `make docs-check`, `make check`, and `make pre-commit`.

Template maintainers verify a disposable render by following the fresh-copy procedure above in a
temporary destination, then removing that destination after review. Dependency-backed generated
checks require `uv`, working GitHub SSH credentials, and network access to the pinned private SDK
source.

The repository provides reproducible source-only smoke targets that create and clean their own
temporary destination:

```bash
make template-copy
make template-check
```

`template-copy` validates the rendered contract structure. `template-check` additionally runs the
generated documentation checker and `compileall`; it does not replace the dependency-backed
fresh-copy or SDK compatibility workflows above.

Report every unavailable tool, failed command, and external-service limitation. Do not claim a
check that was not executed.
