#!/bin/sh
# Build-time SDK source selection only. The uv.lock Git revision stays authoritative.
set -eu
export GIT_CONFIG_COUNT=1 GIT_TERMINAL_PROMPT=0 UV_NO_GITHUB_FAST_PATH=1
export GIT_CONFIG_KEY_0=url.file:///opt/sdk-source/pypokerlost.git.insteadOf
export GIT_CONFIG_VALUE_0=ssh://git@github.com/pokerlost/pypokerlost.git
case "$SDK_SOURCE_MODE" in
    local)
        test -d /opt/sdk-source/pypokerlost.git/objects
        export GIT_ALLOW_PROTOCOL=file
        ;;
    remote)
        test -s /run/secrets/sdk_token
        export GIT_CONFIG_KEY_0=url.https://github.com/pokerlost/pypokerlost.git.insteadOf
        export GIT_ASKPASS=/usr/local/bin/sdk_askpass
        ;;
    *) echo 'SDK_SOURCE_MODE must be remote or local' >&2; exit 1 ;;
esac
exec uv sync --locked --no-install-project "$@"
