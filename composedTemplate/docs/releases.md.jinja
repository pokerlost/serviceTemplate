# Releases

Follow the [shared release policy](https://github.com/serrja/baseRules/blob/8434509933feaa71ba312f8d02caad7362766d5a/docs/releases.md).
Every new push to `dev` or `main`, including documentation changes, requires
successful checks and a GitHub Release at its exact event SHA. Tags use
`vX.Y.Z-dev.N` for dev prereleases and `vX.Y.Z` for stable main releases; Python
metadata uses `X.Y.Z.devN` and `X.Y.Z` respectively. Do not rewrite published tags.

`make release-check` verifies source-bound build metadata without publication.
The generated CI checks native wheel/sdist packages and the exact installed wheel
without building an application image. After its `required` gate, pushes to `dev`
or `main` call the pinned shared Python allocator and publisher. PRs and pushes to
`test` run checks without allocation or publication. A configured workflow is not
evidence that a release was published; inspect the exact event SHA and release.

`docker/python_release.py` supplies an unprivileged native H02 build/receipt
adapter for a reviewed caller of the [pinned Python contract](https://github.com/pokerlost/.github/blob/e5cac33af228224af9deaef308e39c1b9f788033/docs/python_release_contract.md).
It exports clean exact HEAD outside the checkout, injects the allocated static
version with `uv version --frozen --offline`, and builds wheel/sdist offline using
the locked interpreter and its already installed declared backend. The original
pyproject and lock remain unchanged. Run `build --help` and `receipt --help` for
required paths and identities. Pass the pinned provider verifier's ordered JSON
metadata to `receipt` before attestation/upload. The helper does not allocate versions or publish; the generated CI caller uses
the shared provider workflows for those operations. Dynamic versions and in-tree
backends are unsupported. Compiled builds require their actual reviewed wheel
tags rather than a pure-Python tag.

Before promotion, review the full diff, checks and ancestry of working branch →
`test` → `dev` → `main`. Permanent source branches must survive promotion. A
missing or billing-blocked mandatory hosted check blocks merge and publication.
Registry publication and deployment require their own configured destination and
authorization. Preserve prior artifacts and assess database compatibility before
a rollback.

## Native installed acceptance

The caller preserves the committed lock and full SDK Git revision. Both toolchain
and installed environments live outside source and use locked, noneditable
dependency preparation without installing the project. The verified allocated
wheel is installed without dependency resolution. Its exact exported pyproject,
logging configuration, tests, scripts and optional Alembic resources form an
outside-source fixture; no `src/` or source `PYTHONPATH` can satisfy acceptance.
The inherited strict package test proves exact name/version, wheel bytes and
noneditable installed origin before receipt/attestation/upload.

Persistent profiles use a disposable PostgreSQL instance and compare explicit
pytest collection and JUnit to the project-owned `.github/native-integration.json`.
New persistent services start with two technical cases; add the exact existing
service migration cases when adopting this CI. Missing, extra, failed or skipped
cases fail. Copier preserves this owner manifest. Keep ordinary pytest separate
from nonstandard integration filenames. Native package checks do not constitute
private B1 application-image, Kind, deployment or registry acceptance.
