#!/bin/bash
# Run only the reviewed default-branch guard in its locked toolchain.
set -euo pipefail
exec docker run --rm --init --read-only --tmpfs /tmp:rw,mode=1777 \
  --user "$(id -u):$(id -g)" --env GH_CONFIG_DIR=/tmp/gh \
  --env GIT_CONFIG_COUNT=2 --env GIT_CONFIG_KEY_0=safe.directory \
  --env "GIT_CONFIG_VALUE_0=$GITHUB_WORKSPACE/trusted" --env GIT_CONFIG_KEY_1=safe.directory \
  --env "GIT_CONFIG_VALUE_1=$GITHUB_WORKSPACE/candidate" \
  --env GH_TOKEN --env REVIEWED_SHA --env ADMITTED_SHA --env ADMITTED_WORKFLOW_SHA \
  --env OWNER_WRITER_REVIEW --env GITHUB_REPOSITORY --env GITHUB_EVENT_NAME \
  --env GITHUB_ACTOR --env GITHUB_TRIGGERING_ACTOR --env GITHUB_SHA --env GITHUB_REF \
  --mount "type=bind,source=$GITHUB_WORKSPACE,target=$GITHUB_WORKSPACE,readonly" \
  sdk-admission:reviewed "$@"
