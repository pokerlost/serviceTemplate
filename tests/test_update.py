"""Check a real Copier update across committed specialization refs."""

from __future__ import annotations

import io
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
COPIER = [sys.executable, "-m", "copier"]


def _run(*args: str, cwd: Path | None = None) -> str:
    result = subprocess.run(
        list(args), cwd=cwd, capture_output=True, text=True, check=True, timeout=60
    )
    return result.stdout.strip()


def _git(repo: Path, *args: str) -> str:
    return _run("git", *args, cwd=repo)


def _commit(repo: Path, paths: tuple[str, ...], message: str) -> str:
    _git(repo, "add", *paths)
    _git(
        repo,
        "-c",
        "user.name=Template Test",
        "-c",
        "user.email=template-test@example.invalid",
        "commit",
        "--quiet",
        "-m",
        message,
    )
    return _git(repo, "rev-parse", "HEAD")


def test_update_keeps_service_owned_files_and_migrations(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    shutil.copy2(ROOT / "copier.yml", source / "copier.yml")
    shutil.copytree(ROOT / "composedTemplate", source / "composedTemplate")
    _git(source, "init", "--quiet")
    first = _commit(source, ("copier.yml", "composedTemplate"), "base source")

    output = tmp_path / "output"
    _run(
        *COPIER,
        "copy",
        "--quiet",
        "--defaults",
        f"--vcs-ref={first}",
        str(source),
        str(output),
        "-d",
        "service_name=sampleService",
        "-d",
        "withPersistence=true",
        "-d",
        "withCi=false",
    )
    _git(output, "init", "--quiet")
    _commit(output, (".",), "initial render")
    owner_doc = output / "SERVICE.md"
    owner_agents = output / "AGENTS.md"
    owner_agents.write_text(
        owner_agents.read_text() + "\nProject-owned agent boundary.\n"
    )
    original_agents = owner_agents.read_bytes()
    scopes = output / "src/sampleservice/scopes.py"
    revision = output / "migrations/versions/owner_revision.py"
    owner_doc.write_text(owner_doc.read_text() + "\nService owner note.\n")
    scopes.write_text(scopes.read_text() + "\n# exact owner scopes\n")
    revision.write_text('"""Existing migration remains byte-identical."""\n')
    original_revision = revision.read_bytes()
    _commit(
        output,
        (
            "SERVICE.md",
            "AGENTS.md",
            "src/sampleservice/scopes.py",
            "migrations/versions/owner_revision.py",
        ),
        "service-owned files",
    )

    managed = source / "composedTemplate/src/{{ packageName }}/api/health.py.jinja"
    managed.write_text(managed.read_text() + "\n# updated managed health\n")
    second = _commit(
        source,
        ("composedTemplate/src/{{ packageName }}/api/health.py.jinja",),
        "update infrastructure route",
    )
    _run(*COPIER, "update", "--quiet", "--defaults", f"--vcs-ref={second}", cwd=output)
    assert "Service owner note." in owner_doc.read_text()
    assert owner_agents.read_bytes() == original_agents
    assert "# exact owner scopes" in scopes.read_text()
    assert revision.read_bytes() == original_revision
    assert (
        "# updated managed health"
        in (output / "src/sampleservice/api/health.py").read_text()
    )
    assert not _git(output, "ls-files", "-u")
    assert not list(output.rglob("*.rej"))


@pytest.mark.parametrize("persistence", [False, True])
def test_update_from_committed_foundation_preserves_owner_state(
    tmp_path: Path, persistence: bool
) -> None:
    source = tmp_path / "source"
    source.mkdir()
    archive = subprocess.check_output(
        [
            "git",
            "-C",
            str(ROOT),
            "archive",
            "7378c09e4e1e459e7deae5abb2f37e8016776560",
            "copier.yml",
            "composedTemplate",
        ]
    )
    with tarfile.open(fileobj=io.BytesIO(archive)) as bundle:
        bundle.extractall(source, filter="data")
    _git(source, "init", "--quiet")
    first = _commit(source, ("copier.yml", "composedTemplate"), "committed source")
    output = tmp_path / "application"
    _run(
        *COPIER,
        "copy",
        "--quiet",
        "--defaults",
        f"--vcs-ref={first}",
        str(source),
        str(output),
        "-d",
        "service_name=sampleService",
        "-d",
        f"withPersistence={str(persistence).lower()}",
        "-d",
        "withCi=false",
    )
    _git(output, "init", "--quiet")
    _commit(output, (".",), "old render")
    owner_paths = [
        "PROJECT.md",
        "SERVICE.md",
        "src/sampleservice/scopes.py",
        "src/sampleservice/settings.py",
        "tests/test_http.py",
    ]
    preserved: dict[str, bytes] = {}
    for name in owner_paths:
        path = output / name
        suffix = "\n# owner policy\n" if name.endswith(".py") else "\nOwner policy.\n"
        path.write_text(path.read_text() + suffix)
        preserved[name] = path.read_bytes()
    if persistence:
        revision = output / "migrations/versions/owner_revision.py"
        revision.write_text('"""Existing database history must survive update."""\n')
        preserved[revision.relative_to(output).as_posix()] = revision.read_bytes()
    _commit(output, (".",), "owner data")
    shutil.rmtree(source / "composedTemplate")
    shutil.copytree(ROOT / "composedTemplate", source / "composedTemplate")
    shutil.copy2(ROOT / "copier.yml", source / "copier.yml")
    second = _commit(source, ("copier.yml", "composedTemplate"), "new source")
    _run(
        *COPIER,
        "update",
        "--quiet",
        "--defaults",
        f"--vcs-ref={second}",
        "-d",
        "withKubernetes=true",
        cwd=output,
    )
    for name, expected in preserved.items():
        assert (output / name).read_bytes() == expected, name
    assert (output / "tests/foundation/test_authorization.py").is_file()
    assert (output / "deploy/chart/templates/deployment.yaml").is_file()
    assert (output / "compose.test.yaml").is_file() is persistence
    assert not _git(output, "ls-files", "-u")
    assert not list(output.rglob("*.rej"))


@pytest.mark.parametrize("runtime_docker", [False, True])
def test_quality_delivery_uses_the_sdk_recipe_for_each_runtime_choice(
    tmp_path: Path, runtime_docker: bool
) -> None:
    """Quality-only renders keep SDK sync, Helm, artifacts, and isolated DB tests."""
    source = tmp_path / "source"
    source.mkdir()
    shutil.copy2(ROOT / "copier.yml", source / "copier.yml")
    shutil.copytree(ROOT / "composedTemplate", source / "composedTemplate")
    _git(source, "init", "--quiet")
    revision = _commit(source, ("copier.yml", "composedTemplate"), "quality source")
    output = tmp_path / "application"
    _run(
        *COPIER,
        "copy",
        "--quiet",
        "--defaults",
        f"--vcs-ref={revision}",
        str(source),
        str(output),
        "-d",
        "service_name=sampleService",
        "-d",
        "withPersistence=true",
        "-d",
        f"withDocker={str(runtime_docker).lower()}",
        "-d",
        "withCi=false",
    )
    _git(output, "init", "--quiet")
    selected = "Dockerfile" if runtime_docker else "Dockerfile.quality"
    settings = _run(
        "make",
        "--silent",
        "--eval=print-quality:;@echo $(QUALITY_DOCKERFILE) $(BUILD_DOCKERFILE)",
        "print-quality",
        cwd=output,
    )
    assert settings == f"{selected} {selected}"
    recipe = (output / selected).read_text()
    assert "sdk_sync --all-groups" in recipe and "get.helm.sh/helm-" in recipe
    assert "AS test" in recipe and "AS artifacts" in recipe
    assert (output / "compose.test.yaml").exists()
    assert (output / "Dockerfile").exists() == runtime_docker
