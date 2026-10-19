# Reviewed SDK technical acceptance

This CI-only entry point runs `.github/workflows/sdk-acceptance.yml` from the reviewed
default branch. The separately reviewed source is the full SHA input `reviewed_sha`,
checked out under `candidate`; workflow/scripts/actions come from `trusted`, at the
default workflow commit. No feature-branch workflow or local action is executed.

## Admission and credentials

The owner reviews the complete current source diff and the current CI-only PR before
setting `SDK_BUILD_REVIEWED_SHA` to the source SHA and `SDK_WORKFLOW_REVIEWED_SHA` to the
reviewed default-branch commit. Dispatch this workflow on `main`, never on the candidate
branch. A source input is not itself authorization. Both actors must be `serrja`, the
repository must be one of the six private consumers, current PR #1 must have that exact
same-repository head, and the current default commit must match the workflow pin.
Every current writer must still be `serrja`. A changed source/default head fails admission
and requires a new review; changed refs never inherit the earlier authorization.

This is the owner-approved sole-writer model, not independent environment approval.
Repository secrets are available to trusted same-repository workflow authors; reassess
the model before another writer is added. No unavailable server protection is implied.

The only App is the existing `pokerlost-sdk-ci`, installed for SDK-only read access.
`POKERLOST_SDK_APP_ID` and `POKERLOST_SDK_APP_PRIVATE_KEY` are provided only to the pinned
official token action after admission. Its token is narrowed to `pypokerlost` contents
read and automatically revoked at job completion. Reviewed Make/Docker build recipes
receive the short-lived SDK token only for BuildKit secret mounts; application/test
containers do not receive the App key or SDK token. Inputs, secrets and credentials are
never echoed, stored in Git, copied to images or uploaded in evidence. No App installation,
package ACL, repository visibility or branch protection is changed by the workflow.

## Actual acceptance

The default-branch driver `.github/scripts/sdk_acceptance.sh` invokes the existing project
Make/Docker recipes from the exact reviewed source. Those source recipes, Dockerfiles,
build backends and their executed scripts are part of the source review. The source
itself cannot choose a workflow, arbitrary CI action, repository, registry or cluster.
Admission checks are repeated immediately before SDK token creation.

The specialization renders runtime variants with and without PostgreSQL. Each service
uses its existing persistence capability. Fresh source/installed-wheel tests, types,
canonical wheel/sdist, runtime startup/readiness and graceful stop must pass. DB-backed
variants run Alembic upgrade against disposable PostgreSQL. The same loaded runtime image
is used in a task-owned Kind cluster with explicit kubeconfig/context for readiness,
migration, scale and rollback. No working database or remote cluster is selected.

Existing private per-consumer/target/platform owner cache scopes are reused. Test runs
are fresh after cache restoration. The tested image is archived without rebuilding and
retained with reports for 14 days; no image is published. Coverage below 100% remains
advisory. Test/build/type/access/invalid-report errors fail; skipped private acceptance
never makes a manual run successful. No product operation, release, tag or production
deployment belongs to this entry point.

## Review and recovery

PR checks run the admission regression suite in a pinned, read-only networkless Python
container, without SDK credentials, and validate actual workflows with actionlint.
Review all called scripts and actions, not only this YAML. Existing product CI, commands,
coverage policy, Docker recipes and public contracts remain unchanged.

Revoke admission by clearing either reviewed-SHA variable. Revert the CI-only change
with an ordinary commit if needed; do not force push or remove repository branches or
user storage. Use the recorded full source/workflow/image identities when reviewing a
failed run or restoring a previous verified candidate.
