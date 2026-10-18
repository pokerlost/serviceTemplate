# Technical verification

The template maintains real Copier and documentation tests; each render also receives the shared
Python/FastAPI tests plus Pokerlost envelope and authorization tests. Read [creation and updates](../CREATE_SERVICE.md)
for dependency access and [SDK compatibility](../SDK_COMPATIBILITY.md) for the wire boundary.

## Maintainer checks

Run `make install`, `make check` and `make compose`. The locked maintenance environment requires
Python 3.14. Coverage includes every owned tooling module, including unimported modules, while the
canonical propagated `tools/test_composition.py` suite is test code. A missing branch fails the 100%
threshold; retain its diagnostic rather than lowering the gate. The update suite exercises the
actual committed previous foundation and preserves owner-authored documents, settings, scopes,
seed tests and migration bytes. Generated snapshots are refreshed through the parent composer;
never repair their mirrors manually.

## Service tests and lifecycle

A normal synchronous HTTP test opens `with TestClient(application) as client:`. Entering the context
runs lifespan startup; leaving it proves resource disposal. Keep normal server exception propagation
enabled so unexpected failures fail tests. Only an intentional HTTP 500 assertion uses
`raise_server_exceptions=False`; unrelated HTTP or successful assertions do not share that client.

Async database integration uses HTTPX `ASGITransport` and the application's lifespan context in the
same event loop. This avoids moving an async pool between the TestClient thread and a separate
asyncio loop. `make test-unit` measures isolated runtime coverage; `make test` also runs integration
when persistence is enabled. Set `TEST_DATABASE_URL` only to a disposable PostgreSQL instance.
The integration test creates a uniquely named table, proves commit and rollback, checks actual
readiness and removes its own table. A failed connection is not a successful integration check.

The authorization suite uses test-only signed synthetic inputs. It verifies audience and scope,
canonical missing/invalid/expired failures and that rejection precedes the handler. The runtime
foundation still has no production verifier or business route. Service-owned scope catalogs and
settings are preserved by Copier; extend them only for implemented product contracts.

## Artifacts and private runtime checks

The Docker graph exports wheel/sdist and installs that wheel in separate test/runtime targets.
Cache restoration never substitutes for fresh tests. A BuildKit secret is mounted only for locked
SDK acquisition; runtime contains the installed environment and migrations, with no SDK key, uv,
pytest or source checkout. The final process runs without root, supports read-only filesystems
and stops gracefully. `deploy/chart/` is managed by the FastAPI parent; `deploy/values.yaml` is
owned by the service. `make deploy-local` and `make undeploy-local` operate an explicit disposable
Kind contour, never the default host kubeconfig.

Ordinary PR jobs receive no SDK secret. The private candidate requires a full reviewed SHA, a
private destination and the existing reviewer-protected `sdk-build` environment; the owner may
review their own manual run. Keep `POKERLOST_SDK_APP_ID` and `POKERLOST_SDK_APP_PRIVATE_KEY` only
in that environment. The App installation grants `Contents: read` solely on the SDK repository.
A missing or inaccessible gate blocks runtime checks before token creation. Private cache and
artifacts stay within the consumer repository; a skipped private job is not a passing runtime gate.
The workflow does not publish a registry image, release or remote deployment.
