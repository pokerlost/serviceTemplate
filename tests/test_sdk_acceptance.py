"""Exercise trusted archive entrypoints with synthetic files and a Docker stub."""

from __future__ import annotations

import gzip
import hashlib
import os
import subprocess
from pathlib import Path

import pytest

DRIVER = Path(__file__).resolve().parents[1] / ".github/scripts/sdk_acceptance.sh"
SYNTHETIC_IMAGE = b"synthetic tested Docker image tar\n"


@pytest.fixture(params=["accountsService", "serviceTemplate"])
def archive_context(
    tmp_path: Path, request: pytest.FixtureRequest
) -> tuple[Path, dict[str, str], Path]:
    workspace = tmp_path / "workspace with spaces"
    runner = tmp_path / "runner with spaces"
    repository = str(request.param)
    runtime = (
        runner / "private-render-false"
        if repository == "serviceTemplate"
        else workspace / "candidate"
    )
    report = runtime / "coverage/admission"
    report.mkdir(parents=True)
    (report / "runtime-result.txt").write_text("passed\n")
    (report / "kind-result.txt").write_text("passed\n")
    (runtime / "coverage/summary.md").write_text("Synthetic coverage summary\n")
    binary = tmp_path / "bin"
    binary.mkdir()
    docker = binary / "docker"
    docker.write_text(
        "#!/bin/sh\n"
        "set -e\n"
        'printf "%s\\n" "$*" >> "$DOCKER_CALLS"\n'
        'test "$#" -eq 2 && test "$1" = save && test "$2" = "$TEST_IMAGE"\n'
        'printf "synthetic tested Docker image tar\\n"\n'
        'exit "${STUB_DOCKER_EXIT_CODE:-0}"\n'
    )
    docker.chmod(0o755)
    calls = tmp_path / "docker-calls.txt"
    environment = {
        "PATH": str(binary) + os.pathsep + os.defpath,
        "LC_ALL": "C",
        "GITHUB_REPOSITORY": "pokerlost/" + repository,
        "GITHUB_WORKSPACE": str(workspace),
        "B1_PERSISTENCE": "false",
        "RUNNER_TEMP": str(runner),
        "GITHUB_STEP_SUMMARY": str(tmp_path / "step-summary.md"),
        "DOCKER_CALLS": str(calls),
        "TEST_IMAGE": (
            "verifyservice:candidate"
            if repository == "serviceTemplate"
            else "accountsservice:candidate"
        ),
    }
    return runtime, environment, calls


@pytest.mark.parametrize("nested", [False, True])
def test_archive_checksums_regular_files_without_changing_build_artifacts(
    archive_context: tuple[Path, dict[str, str], Path], nested: bool
) -> None:
    runtime, environment, calls = archive_context
    prefix = "content identity/deeper/" if nested else ""
    artifacts = {
        prefix + "package with spaces.whl": b"existing wheel bytes",
        prefix + "package.tar.gz": b"existing sdist bytes",
        prefix + "line\nbreak.txt": b"filename delimiter regression",
        "chart package.tgz": b"existing Helm archive bytes",
    }
    for relative, content in artifacts.items():
        path = runtime / "dist" / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    (runtime / "dist/empty directory").mkdir()

    result = subprocess.run(
        ["bash", str(DRIVER), "archive"], env=environment, capture_output=True
    )

    assert result.returncode == 0, result.stderr.decode()
    assert calls.read_text().splitlines() == ["save " + environment["TEST_IMAGE"]]
    for relative, content in artifacts.items():
        assert (runtime / "dist" / relative).read_bytes() == content
    image = runtime / "dist/runtime-image.docker.tar.gz"
    assert gzip.decompress(image.read_bytes()) == SYNTHETIC_IMAGE
    manifest = runtime / "coverage/admission/distribution-sha256.txt"
    assert str(runtime) not in manifest.read_text()
    expected = set()
    for relative in [*artifacts, image.name]:
        digest = hashlib.sha256((runtime / "dist" / relative).read_bytes()).hexdigest()
        name = "dist/" + relative
        escaped = name.replace("\\", "\\\\").replace("\n", "\\n")
        prefix = "\\" if escaped != name else ""
        expected.add(f"{prefix}{digest}  {escaped}")
    assert set(manifest.read_text().splitlines()) == expected
    assert (Path(environment["GITHUB_STEP_SUMMARY"])).read_text() == (
        "Synthetic coverage summary\n"
    )


@pytest.mark.parametrize("layout", ["missing", "empty", "directories", "image-only"])
def test_archive_requires_build_artifacts_before_exporting_an_image(
    archive_context: tuple[Path, dict[str, str], Path], layout: str
) -> None:
    runtime, environment, calls = archive_context
    distribution = runtime / "dist"
    if layout != "missing":
        distribution.mkdir()
    if layout == "directories":
        (distribution / "empty nested directory").mkdir()
    previous_image = distribution / "runtime-image.docker.tar.gz"
    if layout == "image-only":
        previous_image.write_bytes(b"previous image archive")

    result = subprocess.run(
        ["bash", str(DRIVER), "archive"], env=environment, capture_output=True
    )

    assert result.returncode != 0
    assert not calls.exists()
    assert not (runtime / "coverage/admission/distribution-sha256.txt").exists()
    if layout == "image-only":
        assert previous_image.read_bytes() == b"previous image archive"


@pytest.mark.parametrize("missing", [("runtime",), ("kind",), ("runtime", "kind")])
def test_archive_requires_both_success_markers_before_exporting_an_image(
    archive_context: tuple[Path, dict[str, str], Path], missing: tuple[str, ...]
) -> None:
    runtime, environment, calls = archive_context
    wheel = runtime / "dist/package.whl"
    wheel.parent.mkdir()
    wheel.write_bytes(b"existing wheel bytes")
    for phase in missing:
        (runtime / "coverage/admission" / f"{phase}-result.txt").unlink()

    result = subprocess.run(
        ["bash", str(DRIVER), "archive"], env=environment, capture_output=True
    )

    assert result.returncode != 0
    assert not calls.exists()
    assert not (runtime / "dist/runtime-image.docker.tar.gz").exists()
    assert not (runtime / "coverage/admission/distribution-sha256.txt").exists()
    assert wheel.read_bytes() == b"existing wheel bytes"


def test_archive_docker_save_failure_is_not_a_successful_distribution(
    archive_context: tuple[Path, dict[str, str], Path],
) -> None:
    runtime, environment, calls = archive_context
    wheel = runtime / "dist/package.whl"
    wheel.parent.mkdir()
    wheel.write_bytes(b"existing wheel bytes")
    environment["STUB_DOCKER_EXIT_CODE"] = "17"

    result = subprocess.run(
        ["bash", str(DRIVER), "archive"], env=environment, capture_output=True
    )

    assert result.returncode == 17
    assert calls.read_text().splitlines() == ["save " + environment["TEST_IMAGE"]]
    assert wheel.read_bytes() == b"existing wheel bytes"
    assert not (runtime / "coverage/admission/distribution-sha256.txt").exists()
