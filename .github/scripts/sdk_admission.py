"""Admit one reviewed source commit from a reviewed default-branch workflow."""

from __future__ import annotations

import json
import os
import re
import subprocess
import time
from pathlib import Path
from typing import Annotated, Any, Literal, cast

import typer
from pydantic import BaseModel, ConfigDict, Field, ValidationError

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
    source_commit: dict[str, Any],
    comparison: dict[str, Any],
    pulls: list[dict[str, Any]],
    writers: list[dict[str, Any]],
) -> None:
    """Reject changed refs, fork sources and non-owner/default dispatches."""
    name = env.get("GITHUB_REPOSITORY", "")
    source = env.get("REVIEWED_SHA", "")
    workflow = env.get("GITHUB_SHA", "")
    require(name in CONSUMERS, "Repository is not an SDK CI consumer")
    require(
        env.get("GITHUB_EVENT_NAME") == "workflow_dispatch", "Manual dispatch required"
    )
    require(env.get("GITHUB_ACTOR") == "serrja", "Owner actor required")
    require(env.get("GITHUB_TRIGGERING_ACTOR") == "serrja", "Owner rerun required")
    require(
        FULL_SHA.fullmatch(source) is not None, "Full lowercase source SHA required"
    )
    require(FULL_SHA.fullmatch(workflow) is not None, "Full workflow SHA required")
    require(source == env.get("ADMITTED_SHA"), "Source SHA is not currently admitted")
    require(
        workflow == env.get("ADMITTED_WORKFLOW_SHA"),
        "Default workflow SHA is not currently admitted",
    )
    require(repository.get("full_name") == name, "Repository identity mismatch")
    require(repository.get("private") is True, "Private consumer required")
    branch = repository.get("default_branch")
    require(
        env.get("GITHUB_REF") == "refs/heads/" + str(branch), "Default ref required"
    )
    require(default.get("sha") == workflow, "Default HEAD changed; review it again")
    require(source_commit.get("sha") == source, "Source commit identity mismatch")
    # The commit endpoint belongs to this repository. After merge, admit only an
    # exact ancestor of the current default; before merge require its actual open
    # same-repository PR head, without assuming a particular PR number.
    integrated = (
        comparison.get("status") in {"ahead", "identical"}
        and comparison.get("merge_base_commit", {}).get("sha") == source
    )
    candidate = any(
        pull.get("state") == "open"
        and pull.get("head", {}).get("sha") == source
        and (pull.get("head", {}).get("repo") or {}).get("full_name") == name
        for pull in pulls
    )
    require(
        integrated or candidate,
        "Source is neither integrated nor an exact open local PR HEAD",
    )
    validate_owner_review(env)
    validate_visible_writers(writers)


def validate_visible_writers(writers: list[dict[str, Any]]) -> None:
    """Reject visible additional writers without treating a partial list as proof."""
    require(
        len(writers) < 100, "Collaborator pagination requires an explicit new review"
    )
    write_roles = {"admin", "maintain", "write"}
    known_roles = write_roles | {"read", "triage", "triage_plus"}
    for user in writers:
        role = user.get("role_name")
        require(role in known_roles, "Unknown collaborator role requires review")
        require(
            not user["permissions"]["push"] or role in write_roles,
            "Inconsistent collaborator role requires review",
        )
    write_logins = {
        user["login"] for user in writers if user["role_name"] in write_roles
    }
    require(write_logins <= {"serrja"}, "Sole-writer assumption changed")


class OwnerReview(BaseModel):
    """Pure receipt structure; time and server authorization are checked separately."""

    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)
    repository: str
    actor: Literal["serrja"]
    source: Annotated[str, Field(pattern=r"^[0-9a-f]{40}$")]
    workflow: Annotated[str, Field(pattern=r"^[0-9a-f]{40}$")]
    reviewed_at: Annotated[int, Field(strict=True, ge=0)]


def validate_owner_review(env: dict[str, str]) -> None:
    """Require a fresh owner writer audit bound to this repository and commit pair."""
    fields = env.get("OWNER_WRITER_REVIEW", "").split("|")
    require(len(fields) == 5, "Owner writer review required")
    require(fields[4].isdecimal(), "Owner writer review timestamp is invalid")
    try:
        review = OwnerReview.model_validate(
            dict(
                repository=fields[0],
                actor=fields[1],
                source=fields[2],
                workflow=fields[3],
                reviewed_at=int(fields[4]),
            )
        )
    except ValidationError:
        raise ValueError("Owner writer review structure is invalid") from None
    require(
        (review.repository, review.source, review.workflow)
        == (
            env.get("GITHUB_REPOSITORY"),
            env.get("REVIEWED_SHA"),
            env.get("GITHUB_SHA"),
        ),
        "Owner writer review required for this exact repository/source/workflow",
    )
    age = time.time() - review.reviewed_at
    require(0 <= age <= 3600, "Owner writer review expired or is in the future")


def api(endpoint: str) -> object:
    """Read admission metadata without echoing API payloads or credentials."""
    result = subprocess.run(
        ["gh", "api", endpoint],
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode:
        raise RuntimeError("GitHub admission API failed: " + endpoint)
    return json.loads(result.stdout)


def admit(trusted: Path | None, candidate: Path | None) -> None:
    """Read current server metadata and verify optional exact checkout roots."""
    env = dict(os.environ)
    name = env.get("GITHUB_REPOSITORY", "")
    require(name in CONSUMERS, "Repository is not an SDK CI consumer")
    source = env.get("REVIEWED_SHA", "")
    require(
        FULL_SHA.fullmatch(source) is not None, "Full lowercase source SHA required"
    )
    repository = cast(dict[str, Any], api("repos/" + name))
    default = cast(
        dict[str, Any],
        api("repos/" + name + "/commits/" + repository["default_branch"]),
    )
    source_commit = cast(dict[str, Any], api("repos/" + name + "/commits/" + source))
    comparison = cast(
        dict[str, Any],
        api("repos/" + name + "/compare/" + source + "..." + default["sha"]),
    )
    pulls = cast(
        list[dict[str, Any]],
        api("repos/" + name + "/commits/" + source + "/pulls?per_page=100"),
    )
    require(len(pulls) < 100, "Source PR pagination requires explicit review")
    writers = cast(
        list[dict[str, Any]], api("repos/" + name + "/collaborators?per_page=100")
    )
    validate(env, repository, default, source_commit, comparison, pulls, writers)
    require(
        (trusted is None) == (candidate is None),
        "Pass both trusted and candidate directories",
    )
    if trusted is not None and candidate is not None:
        for directory, expected in ((trusted, env["GITHUB_SHA"]), (candidate, source)):
            root = directory.resolve()
            actual = subprocess.check_output(
                ["git", "-C", str(root), "rev-parse", "HEAD"], text=True
            ).strip()
            require(actual == expected, "Checkout SHA mismatch")
            top = subprocess.check_output(
                ["git", "-C", str(root), "rev-parse", "--show-toplevel"], text=True
            ).strip()
            require(Path(top).resolve() == root, "Exact checkout root required")


app = typer.Typer(pretty_exceptions_show_locals=False)


@app.command()
def main(
    trusted: Annotated[Path | None, typer.Argument()] = None,
    candidate: Annotated[Path | None, typer.Argument()] = None,
) -> None:
    """Admit reviewed commits; SDK credentials are never read by this command."""
    try:
        admit(trusted, candidate)
    except ValueError, RuntimeError, subprocess.SubprocessError:
        typer.echo(
            "SDK admission failed; recheck identities, source and owner review",
            err=True,
        )
        raise typer.Exit(1) from None
    typer.echo("Admitted exact source/default commits; SDK secrets not read")


if __name__ == "__main__":
    app()
