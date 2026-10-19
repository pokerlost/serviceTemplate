"""Admit one reviewed source commit from a reviewed default-branch workflow."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, cast

CONSUMERS = {
    "pokerlost/serviceTemplate",
    "pokerlost/authService",
    "pokerlost/accountsService",
    "pokerlost/virtualMoney",
    "pokerlost/pokerService",
    "pokerlost/cryptoService",
}
FULL_SHA = re.compile(r"[0-9a-f]{40}\Z")


def require(condition: bool, message: str) -> None:
    """Fail closed when an admission invariant does not hold."""
    if not condition:
        raise ValueError(message)


def validate(
    env: dict[str, str],
    repository: dict[str, Any],
    default: dict[str, Any],
    pull: dict[str, Any],
    writers: list[dict[str, Any]],
) -> None:
    """Reject changed refs, fork sources and non-owner/default dispatches."""
    name = env.get("GITHUB_REPOSITORY", "")
    source = env.get("REVIEWED_SHA", "")
    workflow = env.get("GITHUB_SHA", "")
    require(name in CONSUMERS, "Repository is not an SDK CI consumer")
    require(env.get("GITHUB_EVENT_NAME") == "workflow_dispatch", "Manual dispatch required")
    require(env.get("GITHUB_ACTOR") == "serrja", "Owner actor required")
    require(env.get("GITHUB_TRIGGERING_ACTOR") == "serrja", "Owner rerun required")
    require(FULL_SHA.fullmatch(source) is not None, "Full lowercase source SHA required")
    require(FULL_SHA.fullmatch(workflow) is not None, "Full workflow SHA required")
    require(source == env.get("ADMITTED_SHA"), "Source SHA is not currently admitted")
    require(
        workflow == env.get("ADMITTED_WORKFLOW_SHA"),
        "Default workflow SHA is not currently admitted",
    )
    require(repository.get("full_name") == name, "Repository identity mismatch")
    require(repository.get("private") is True, "Private consumer required")
    branch = repository.get("default_branch")
    require(env.get("GITHUB_REF") == "refs/heads/" + str(branch), "Default ref required")
    require(default.get("sha") == workflow, "Default HEAD changed; review it again")
    require(pull.get("state") == "open", "Main source PR must remain open")
    require(pull["head"]["repo"]["full_name"] == name, "Fork source is not admitted")
    require(pull["head"]["sha"] == source, "Source PR HEAD changed; review it again")
    validate_writers(writers)


def validate_writers(writers: list[dict[str, Any]]) -> None:
    """Require one writer using effective roles, including organization grants."""
    require(len(writers) < 100, "Collaborator pagination requires an explicit new review")
    write_roles = {"admin", "maintain", "write"}
    known_roles = write_roles | {"read", "triage", "triage_plus"}
    for user in writers:
        role = user.get("role_name")
        require(role in known_roles, "Unknown collaborator role requires review")
        require(
            not user["permissions"]["push"] or role in write_roles,
            "Inconsistent collaborator role requires review",
        )
    write_logins = {user["login"] for user in writers if user["role_name"] in write_roles}
    require(write_logins == {"serrja"}, "Sole-writer assumption changed")


def api(endpoint: str) -> object:
    """Read admission metadata without echoing API payloads or credentials."""
    result = subprocess.run(
        ["gh", "api", endpoint],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode:
        raise RuntimeError("GitHub admission API failed: " + endpoint)
    return json.loads(result.stdout)


def main() -> None:
    """Validate current server identities and optionally both exact checkouts."""
    env = dict(os.environ)
    name = env.get("GITHUB_REPOSITORY", "")
    require(name in CONSUMERS, "Repository is not an SDK CI consumer")
    repository = cast(dict[str, Any], api("repos/" + name))
    default = cast(
        dict[str, Any],
        api("repos/" + name + "/commits/" + repository["default_branch"]),
    )
    pull = cast(dict[str, Any], api("repos/" + name + "/pulls/1"))
    writers = cast(
        list[dict[str, Any]],
        api("repos/" + name + "/collaborators?per_page=100"),
    )
    validate(env, repository, default, pull, writers)
    if len(sys.argv) == 3:
        for directory, expected in zip(
            sys.argv[1:], [env["GITHUB_SHA"], env["REVIEWED_SHA"]], strict=True
        ):
            root = Path(directory).resolve()
            actual = subprocess.check_output(
                ["git", "-C", str(root), "rev-parse", "HEAD"], text=True
            ).strip()
            require(actual == expected, "Checkout SHA mismatch")
            top = subprocess.check_output(
                ["git", "-C", str(root), "rev-parse", "--show-toplevel"], text=True
            ).strip()
            require(Path(top).resolve() == root, "Exact checkout root required")
    else:
        require(len(sys.argv) == 1, "Pass both trusted and candidate directories")
    sys.stdout.write("Admitted exact source/default commits; SDK secrets not read\n")


if __name__ == "__main__":
    main()
