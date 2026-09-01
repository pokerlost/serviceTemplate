# Create and Update a Pokerlost Service

This document defines the Copier copy, update, and verification workflow. The generated-content
contract is in `TEMPLATE.md`.

## Fresh copy

1. Read `AGENTS.md`, `TEMPLATE.md`, `SDK_COMPATIBILITY.md`, and `copier.yml`.
2. Resolve the destination and the only answer, `service_name`.
3. Run pinned Copier without trusted template execution:

```bash
uvx --from 'copier==9.17.2' copier copy <template-source> <destination> \
  -d service_name=<SERVICE_NAME>
```

4. Inspect `.copier-answers.yml`; do not edit it manually.
5. Read generated `AGENTS.md`, `SERVICE.md`, and `README.md`. Replace only authoritative
   service-specific `SERVICE.md` sections.
6. Confirm normal GitHub SSH access can read the private `pypokerlost` repository. Never place a
   private key or access credential in the generated repository.

## Fresh-copy verification

Confirm the generated repository contains the flat root/OpenAPI routers, body-authorization
dependency, empty scope catalog, verifier port, complete docs tree, Makefile, Helm chart, and
Copier answers. Then run:

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

Verify the pristine endpoints through the real lifespan:

- `GET /` has operation ID `getRoot`, no body, and returns `PokerlostResponse[None]`;
- `GET /getOpenApi` has operation ID `getOpenApi`, no body, and returns the unmodified FastAPI
  document inside `PokerlostResponse`;
- built-in schema/documentation routes are disabled;
- no project OpenAPI extension, service identity, or misleading security scheme exists;
- no response or request correlation metadata is exposed as a public transport contract.

Inspect runtime composition and confirm it contains no fake verifier, outbound client, credentials,
token store, retry tuning, or business operation. `ApplicationResources.token_verifier` is null in
the pristine application and a protected route would therefore fail closed.

Inspect `pyproject.toml` and `uv.lock`: `pypokerlost` must resolve from the private SSH Git source at
the immutable revision documented in `SDK_COMPATIBILITY.md`. Neither file may contain a sibling
path, local file source, credential, or floating branch.

For the body protocol, generator, middleware, scope, OpenAPI, privacy, and negative probes, follow
the complete procedure in `SDK_COMPATIBILITY.md`. Temporary protected routes and disposable local
verifiers must be removed after verification.

When Docker is available, verify the private dependency build:

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

The runtime image must contain no SSH material or build-only Git tooling. The generated ClusterIP
is internal and must remain behind mandatory production HTTPS/TLS termination.

## Template update

Run updates from a generated repository with valid Copier metadata:

```bash
uvx --from 'copier==9.17.2' copier check-update
uvx --from 'copier==9.17.2' copier update
```

For every managed-file change:

1. render a service from the exact prior template commit;
2. modify its service-owned `SERVICE.md` and retain representative service handlers/migrations;
3. update from the new template revision;
4. confirm template-owned files update and obsolete unchanged files disappear;
5. confirm `SERVICE.md`, service behavior, migrations, and service scope values remain unchanged;
6. confirm the flat router/body-auth foundation is present;
7. repeat documentation, compile, quality, OpenAPI, and SDK compatibility checks.

The repository provides source-only disposable smoke targets:

```bash
make template-copy
make template-check
```

They do not replace dependency-backed SDK or runtime verification. Report every unavailable tool,
failed command, and environment limitation.
