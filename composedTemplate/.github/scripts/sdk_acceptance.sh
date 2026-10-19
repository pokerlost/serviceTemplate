#!/bin/bash
# Trusted default-branch driver; existing project Make/Docker recipes own builds/tests.
set -euo pipefail

case "$GITHUB_REPOSITORY" in
  pokerlost/serviceTemplate) package=verifyservice ;;
  pokerlost/authService) package=authservice ;;
  pokerlost/accountsService) package=accountsservice ;;
  pokerlost/virtualMoney) package=virtualmoney ;;
  pokerlost/pokerService) package=pokerservice ;;
  pokerlost/cryptoService) package=cryptoservice ;;
  *) echo 'Unapproved CI consumer' >&2; exit 2 ;;
esac
case "$B1_PERSISTENCE" in true|false) ;; *) exit 2 ;; esac
candidate="$GITHUB_WORKSPACE/candidate"
runtime="$candidate"
if [ "$GITHUB_REPOSITORY" = pokerlost/serviceTemplate ]; then
  runtime="$RUNNER_TEMP/private-render-$B1_PERSISTENCE"
fi
report="$runtime/coverage/admission"
secret_args='--secret id=sdk_token,env=SDK_APP_TOKEN'
postgres='postgres:17.11-trixie@sha256:2d2b8998d31037bf721cfdf764d76ba74171b4fab3431b7f72c27c56ddbdf9e3'
node='kindest/node:v1.37.0@sha256:a1ed56cfb0e7b93589bdf97c8cd566405a265939e3620fc4f5de89adff580ae5'

case "${1:-}" in
  prepare)
    if [ "$runtime" != "$candidate" ]; then
      make -C "$candidate" render RENDER_OUTPUT="$runtime" \
        RENDER_ARGS="-d service_name=verifyService -d withPersistence=$B1_PERSISTENCE -d withDocker=true -d withKubernetes=true"
    fi
    mkdir -p "$report" "$runtime/dist"
    printf 'runtime_dir=%s\npackage=%s\n' "$runtime" "$package" >> "$GITHUB_OUTPUT"
    printf '%s\n' "$REVIEWED_SHA" > "$report/source-sha.txt"
    printf '%s\n' "$GITHUB_SHA" > "$report/workflow-sha.txt"
    ;;
  lock)
    if [ "$runtime" != "$candidate" ]; then
      make -C "$candidate" lock-render SDK_RENDER="$runtime"
    fi
    ;;
  check|build|verify)
    make -C "$runtime" "$1" QUALITY_NETWORK=host DOCKER_BUILD_ARGS="$secret_args"
    ;;
  runtime)
    mkdir -p "$report"
    docker image inspect "$package:candidate" --format '{{.Id}}' > "$report/image-id.txt"
    database_args=()
    if [ "$B1_PERSISTENCE" = true ]; then
      database_args=(--env DATABASE_URL=postgresql+asyncpg://ci:ci@127.0.0.1:5432/ci)
      docker run --rm --read-only --tmpfs /tmp:rw,noexec,nosuid,size=64m \
        --network host "${database_args[@]}" "$package:candidate" \
        python -m alembic upgrade head > "$report/alembic-upgrade.log" 2>&1
      docker run --rm --interactive --read-only --tmpfs /tmp:rw,noexec,nosuid,size=64m \
        --network host "${database_args[@]}" "$package:candidate" \
        python - "$package" > "$report/migration-status.json" <<'PYTHON'
import asyncio
import importlib
import os
import sys
from alembic.config import Config
from sqlalchemy.ext.asyncio import create_async_engine
read_heads = importlib.import_module(sys.argv[1] + ".migration_status").read_heads
async def inspect():
    engine = create_async_engine(os.environ["DATABASE_URL"])
    try:
        async with engine.connect() as connection:
            status = await connection.run_sync(lambda sync: read_heads(Config("alembic.ini"), sync))
        print(status.model_dump_json(by_alias=True))
    finally:
        await engine.dispose()
asyncio.run(inspect())
PYTHON
      jq -e '.expectedHeads == .currentHeads' "$report/migration-status.json" >/dev/null
      jq -r '.expectedHeads[]' "$report/migration-status.json" | sort > "$report/expected-revisions.txt"
    fi
    container=''
    trap 'if [ -n "$container" ]; then docker rm -f "$container" >/dev/null; fi' EXIT
    container=$(docker run --detach --read-only --tmpfs /tmp:rw,noexec,nosuid,size=64m \
      --network host "${database_args[@]}" "$package:candidate")
    ready=false
    for _ in $(seq 1 45); do
      if curl --fail --silent http://127.0.0.1:8000/health/ready > "$report/readiness.json"; then
        ready=true; break
      fi
      sleep 1
    done
    test "$ready" = true
    curl --fail --silent http://127.0.0.1:8000/ > "$report/root.json"
    curl --fail --silent http://127.0.0.1:8000/getOpenApi > "$report/openapi.json"
    docker stop --time 15 "$container"
    test "$(docker inspect --format '{{.State.ExitCode}}' "$container")" = 0
    printf '%s\n' passed > "$report/runtime-result.txt"
    ;;
  kind)
    cluster="$package-b1-$GITHUB_RUN_ID-$GITHUB_RUN_ATTEMPT-$B1_PERSISTENCE"
    kubeconfig="$RUNNER_TEMP/$cluster.kubeconfig"
    context="kind-$cluster"
    forward_pid=''
    cleanup() {
      if [ -n "$forward_pid" ]; then kill "$forward_pid" 2>/dev/null || :; fi
      kind delete cluster --name "$cluster"
    }
    trap cleanup EXIT
    test "$(docker image inspect "$package:candidate" --format '{{.Id}}')" = "$(cat "$report/image-id.txt")"
    kind create cluster --name "$cluster" --image "$node" --kubeconfig "$kubeconfig" --wait 180s
    kind load docker-image "$package:candidate" --name "$cluster"
    kubectl --kubeconfig "$kubeconfig" --context "$context" create namespace foundation
    database_values=()
    if [ "$B1_PERSISTENCE" = true ]; then
      docker pull "$postgres"
      docker tag "$postgres" foundation-postgres:local-2d2b8998d310
      kind load docker-image foundation-postgres:local-2d2b8998d310 --name "$cluster"
      kubectl --kubeconfig "$kubeconfig" --context "$context" -n foundation apply -f "$runtime/deploy/local/postgres.yaml"
      kubectl --kubeconfig "$kubeconfig" --context "$context" -n foundation rollout status deployment/foundation-database --timeout=180s
      database_values=(--set database.secretName=foundation-database --set migration.enabled=true)
    fi
    helm upgrade --install "$package" "$runtime/deploy/chart" \
      --kubeconfig "$kubeconfig" --kube-context "$context" --namespace foundation \
      --wait --timeout 180s --rollback-on-failure --values "$runtime/deploy/values.yaml" \
      --set image.repository="$package" --set image.tag=candidate --set localDevelopment=true \
      "${database_values[@]}" > "$report/kind-install.log" 2>&1
    if [ "$B1_PERSISTENCE" = true ]; then
      kubectl --kubeconfig "$kubeconfig" --context "$context" -n foundation \
        exec -i "deployment/$package" -- python - "$package" > "$report/kind-migration-status.json" <<'PYTHON'
import asyncio
import importlib
import os
import sys
from alembic.config import Config
from sqlalchemy.ext.asyncio import create_async_engine
read_heads = importlib.import_module(sys.argv[1] + ".migration_status").read_heads
async def inspect():
    engine = create_async_engine(os.environ["DATABASE_URL"])
    try:
        async with engine.connect() as connection:
            status = await connection.run_sync(lambda sync: read_heads(Config("alembic.ini"), sync))
        print(status.model_dump_json(by_alias=True))
    finally:
        await engine.dispose()
asyncio.run(inspect())
PYTHON
      jq -e '.expectedHeads == .currentHeads' "$report/kind-migration-status.json" >/dev/null
      jq -r '.currentHeads[]' "$report/kind-migration-status.json" | sort > "$report/actual-kind-revisions.txt"
      cmp "$report/expected-revisions.txt" "$report/actual-kind-revisions.txt"
    fi
    helm upgrade "$package" "$runtime/deploy/chart" --kubeconfig "$kubeconfig" \
      --kube-context "$context" --namespace foundation --reuse-values --set replicaCount=3 \
      --wait --timeout 180s --rollback-on-failure > "$report/kind-scale.log" 2>&1
    helm rollback "$package" 1 --kubeconfig "$kubeconfig" --kube-context "$context" \
      --namespace foundation --wait --timeout 180s > "$report/kind-rollback.log" 2>&1
    test "$(kubectl --kubeconfig "$kubeconfig" --context "$context" -n foundation \
      get deployment "$package" -o jsonpath='{.spec.replicas}')" = 2
    kubectl --kubeconfig "$kubeconfig" --context "$context" -n foundation \
      port-forward --address=127.0.0.1 "service/$package" 18080:8000 > "$report/port-forward.log" 2>&1 &
    forward_pid=$!
    ready=false
    for _ in $(seq 1 45); do
      if curl --fail --silent http://127.0.0.1:18080/health/ready > "$report/kind-readiness.json"; then
        ready=true; break
      fi
      sleep 1
    done
    test "$ready" = true
    test "$(docker image inspect "$package:candidate" --format '{{.Id}}')" = "$(cat "$report/image-id.txt")"
    helm package "$runtime/deploy/chart" --destination "$runtime/dist"
    printf '%s\n' passed > "$report/kind-result.txt"
    ;;
  archive)
    test -f "$report/runtime-result.txt" && test -f "$report/kind-result.txt"
    docker save "$package:candidate" | gzip --no-name > "$runtime/dist/runtime-image.docker.tar.gz"
    sha256sum "$runtime"/dist/* > "$report/distribution-sha256.txt"
    cat "$runtime/coverage/summary.md" >> "$GITHUB_STEP_SUMMARY"
    if [ -f "$runtime/coverage/installed/summary.md" ]; then
      cat "$runtime/coverage/installed/summary.md" >> "$GITHUB_STEP_SUMMARY"
    fi
    ;;
  *) echo 'Unknown acceptance phase' >&2; exit 2 ;;
esac
