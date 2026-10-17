# Migrate a flat-layout service

This guide covers the reviewed move from the former `app/` Copier source to the composed `src/<packageName>/` source, where `packageName` is derived as lowercase from `service_name`. It does not apply a database migration or move an existing service automatically.

## 🧭 Verified boundary

Copier 9.17.2 was exercised between real Git refs. The first flat-layout migration compared historical `serviceTemplate` commit `7ee12327c5de02d6f1ca43722f959e79e0916de6` with `0d93c7beda9dc93318db138d9bcd301b60927fc5`. The later PEP 8/FastAPI foundation source is `a92abe42ce9c6124adf85f09a35e2b2a29aa481c`; its branch was pushed, but no release tag was created. Disposable updates carried a Python-base edit through both derivatives into a generated service without replacing project-owned content.

The historical update preserved service-owned `SERVICE.md`, `PROJECT.md`, old `app/` code and scopes, and `alembic/` revisions. The current `copier.yml` excludes the legacy `app/`, `alembic/`, and `deploy/` paths while Copier reconstructs the old render; without these exclusions, Copier deleted a modified legacy scopes file. The update adds the new `src/<packageName>/` package. It does not port the old application, settings policy, scopes, or revision graph into that package.

These legacy exclusions are a migration guard. Review their removal only after all dependent flat-layout services have been migrated and their historical data is recoverable.

Isolated copies of `authService` and `accountsService` exposed conflicts in `AGENTS.md`, `README.md`, and `alembic.ini`; auth also conflicted in `pyproject.toml`. Copier proposed removal of 29 prior managed files per service. Each proposed file was compared with the historical render, restored for review, and retained or rewritten where it still carried project-specific guidance or the existing documentation checker. No conflict was resolved by taking an entire side. A zero Copier exit status alone did not mean the index was ready.

The reviewed file migration was then applied to both working services from the committed source. Their answer files were written by Copier, with `withPersistence=true`; the project-specific reconciliation was copied from the verified isolated result. The old flat `app/` and `alembic/` trees were moved to a private recovery area before removal from the active checkout. Five auth and three accounts revision files are byte-identical under `migrations/versions/` (`R100` in the Git diff). The prior foundation commit in each service also retains the tracked flat implementation. Service-owned docs, empty exact scope catalogs, and existing CI workflows were retained. No business route was restored.

## 🔁 Reviewed procedure

1. Preserve the complete current tracked diff, necessary untracked files, modes, and historical revisions outside the service repository. Record its current Git index and source answers. Keep a restoration path before starting.
2. Select reviewed, committed source refs for each template layer. Refresh the Python base, then the FastAPI snapshot and derivative, then this template's FastAPI snapshot and derivative. Review `composition.lock.json` after each refresh. Do not present a dirty worktree as a published ref.
3. In a disposable copy of the service, keep the actual `.copier-answers.yml` and run the update from that copy's root. For an existing database-backed auth or accounts service, explicitly retain persistence:

   ```bash
   uv run --no-project --with 'copier==9.17.2' copier update \
     --defaults --vcs-ref=<reviewed-service-template-ref> \
     -d withPersistence=true .
   git status --short
   git diff --check
   ```

4. Resolve every `UU` path and conflict marker. Review every deletion. Keep `SERVICE.md`, `PROJECT.md`, application code, settings, scopes, local deployment policy, and migrations under the service's ownership. Port intended runtime code into `src/<packageName>/` one responsibility at a time; remove old flat modules only after their consumers and replacement behavior are checked. Do not register a business route merely to retain an old file.
5. Preserve the historical Alembic revision graph byte-for-byte when moving it to `migrations/versions/`; update `alembic.ini` and the new environment wiring without rewriting an applied revision. Do not run an upgrade or autogenerate against a live database or assume the new metadata drops old tables. Design any schema transition separately against a disposable database.
6. Run the service's permitted package, import, startup, and HTTP checks. Review the complete diff and only then apply the same resolved migration to the working checkout under its own authorization. Copier writes the new answer stamp as part of that real update; do not edit the stamp to anticipate it.

## 📦 Recovery and status

If the disposable update conflicts, preserve its output for review and start another isolated copy from the recorded service snapshot. Restore a working service from its private pre-update backup and original Git state if an authorized migration fails. A template update is not a database rollback.

Current status: both database-backed working migrations are committed after review. Local Ruff, strict mypy, documentation, lock, Alembic history, wheel/sdist, and infrastructure HTTP checks passed. The new workflows configure a disposable PostgreSQL upgrade and positive readiness test, but these jobs have not been read back on the new SHAs. Docker image builds and the manual private SDK stage remain unverified. Technical/regression tests are enabled; no business behavior or live database migration was added.

`pokerService`, `cryptoService`, `authService`, and `virtualMoney` used real Copier updates to the reviewed service source. `accountsService` adopted a fresh render from the canonical remote URL after its historical relative source was proven unsuitable for standalone update; it then passed a repeated standalone update. `pokerClient` adopted the Python-base source separately. Copier recorded the new refs; the answer stamps were not edited by hand. Rehearse later revisions in isolated copies and review project-owned files before updating a working checkout.
