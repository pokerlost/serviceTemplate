"""Check a real Copier update across committed specialization refs."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

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
    assert "# exact owner scopes" in scopes.read_text()
    assert revision.read_bytes() == original_revision
    assert (
        "# updated managed health"
        in (output / "src/sampleservice/api/health.py").read_text()
    )
    assert not _git(output, "ls-files", "-u")
    assert not list(output.rglob("*.rej"))
