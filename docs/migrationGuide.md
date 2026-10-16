# Migrate a flat-layout service

This guide covers the reviewed move from the former `app/` Copier source to the composed `src/<service_name>/` source. It does not apply a database migration or move an existing service automatically.

## 🧭 Verified boundary

Copier 9.17.2 was exercised between two real local Git refs in disposable repositories. The first revision came from the historical `serviceTemplate` HEAD `7ee1232`; the second was committed only in the disposable repository from the current worktree source. A separate end-to-end probe carried a Python-base edit through the FastAPI derivative and this derivative into a generated service with `copier update`. These refs are verification artifacts, not releases or working-repository commits.

The historical update preserved service-owned `SERVICE.md`, `PROJECT.md`, old `app/` code and scopes, and `alembic/` revisions. The current `copier.yml` excludes the legacy `app/`, `alembic/`, and `deploy/` paths while Copier reconstructs the old render; without these exclusions, Copier deleted a modified legacy scopes file. The update adds the new `src/<service_name>/` package. It does not port the old application, settings policy, scopes, or revision graph into that package.

These legacy exclusions are a migration guard. Review their removal only after all dependent flat-layout services have been migrated and their historical data is recoverable.

Isolated copies of the current dirty `authService` and `accountsService` checkouts also completed an update with `withPersistence=true`. Copier reported unresolved conflicts in `AGENTS.md`, `README.md`, and `alembic.ini`; `authService` also conflicted in `pyproject.toml`. It proposed removal of 29 prior managed files in each copy. No update was applied to either working checkout, and their answer stamps remain unchanged. A zero Copier exit status did not mean the conflicting Git index was ready to commit.

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

4. Resolve every `UU` path and conflict marker. Review every deletion. Keep `SERVICE.md`, `PROJECT.md`, application code, settings, scopes, local deployment policy, and migrations under the service's ownership. Port intended runtime code into `src/<service_name>/` one responsibility at a time; remove old flat modules only after their consumers and replacement behavior are checked. Do not register a business route merely to retain an old file.
5. Treat old `alembic/versions/` and new `migrations/` as distinct histories. Do not run an upgrade or autogenerate against a live database, rewrite an applied revision, or assume the new metadata drops old tables. Design any schema transition separately against a disposable database.
6. Run the service's permitted package, import, startup, and HTTP checks. Review the complete diff and only then apply the same resolved migration to the working checkout under its own authorization. Copier writes the new answer stamp as part of that real update; do not edit the stamp to anticipate it.

## 📦 Recovery and status

If the disposable update conflicts, preserve its output for review and start another isolated copy from the recorded service snapshot. Restore a working service from its private pre-update backup and original Git state if an authorized migration fails. A template update is not a database rollback.

Current status: source generation and disposable update are verified; `authService` and `accountsService` working-tree migration is pending conflict resolution and runtime review. The repository's existing CI has not run on this worktree, and the target Pokerlost test/CI rollout is not enabled by this guide.

New local foundations generated from an uncommitted template worktree have a valid content stamp but their Copier `_commit` is not a ref in the working template repository. A direct `copier update` on an isolated copy of `pokerService` failed when Git could not check out that recorded short ref. The same unreleased-source condition applies to the locally generated `cryptoService` and Python-base `pokerClient`. Do not hand-edit their answers to claim another origin. After an authorized source commit exists, rehearse Copier's `recopy` in an isolated copy, compare all project-owned files and the generated answers, then adopt a reviewed result under the service's own authorization.
