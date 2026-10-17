# serviceTemplate

A Pokerlost Copier specialization assembled from a pinned `fastApiTemplate` source, which itself is derived from the existing Python base. The active source is `composedTemplate/`; `foundationOverlay/` owns Pokerlost additions. The former flat template remains reproducible from the repository's historical Git ref `7ee1232`; it is no longer a second worktree source.

## 🚀 Generate

Use Copier 9.17.2 from the repository root. A dirty local source records a worktree render, not a published immutable release.

```bash
destination="$(mktemp -d)"
uv run --no-project --with 'copier==9.17.2' copier copy . "$destination" \
  -d service_name=exampleService
cd "$destination"
uv lock
uv sync --locked
uv run --locked uvicorn exampleservice.app:create_app --factory --host 127.0.0.1 --port 8000
```

The default has no DSN or outbound credential. It has only root, OpenAPI, liveness, and readiness infrastructure routes; no business operation or local token verifier is configured. Local installation of the pinned private `pypokerlost` runtime dependency needs Git SSH read access. New renders include focused technical tests, CI source checks, and a backend Dockerfile. Private SDK checks need the narrow GitHub App access and review gate described in [creation and update](CREATE_SERVICE.md).

## 🧭 Maintenance

`composition.toml` declares the exact inherited files and the overlay ownership. `_sources/fastApiTemplate/sourceIdentity.json` and `composition.lock.json` record the actual parent content identity and generated-file ownership. Refreshing a parent is explicit:

```bash
uv run --no-project --with 'copier==9.17.2' python _sources/fastApiTemplate/tools/compose_template.py --repo . --smoke
uv run --no-project --with 'copier==9.17.2' python _sources/fastApiTemplate/tools/compose_template.py --repo . \
  --refresh-base /path/to/fastApiTemplate --smoke
```

Review the derivative diff before generating or updating downstream services. `SERVICE.md`, `PROJECT.md`, application code, scopes, and migrations remain service-owned. The [template contract](TEMPLATE.md), [SDK compatibility](SDK_COMPATIBILITY.md), [creation/update guide](CREATE_SERVICE.md), and [flat-layout migration guide](docs/migrationGuide.md) define the active behavior. No commit, release, or deployment follows from local generation.
