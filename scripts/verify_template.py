#!/usr/bin/env python3
"""Verify a disposable service generated from the current working template."""

from __future__ import annotations

import argparse
import shlex
import shutil
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

COPIER_VERSION = "9.17.2"
SERVICE_NAME = "templateVerification"
REPOSITORY_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_DOCUMENTS = frozenset(
    {
        "docs/index.md",
        "docs/getting-started/installation.md",
        "docs/getting-started/quickstart.md",
        "docs/getting-started/configuration.md",
        "docs/api/overview.md",
        "docs/api/operation-contract.md",
        "docs/api/application-response.md",
        "docs/api/errors.md",
        "docs/api/openapi-and-sdk.md",
        "docs/api/public-surface.md",
        "docs/architecture/overview.md",
        "docs/architecture/request-lifecycle.md",
        "docs/architecture/persistence-and-transactions.md",
        "docs/development/commands.md",
        "docs/development/contributing.md",
        "docs/development/python-style.md",
        "docs/development/documentation-style.md",
        "docs/development/database-migrations.md",
        "docs/development/containers-and-kubernetes.md",
        "docs/project/quality.md",
        "docs/project/status.md",
    },
)
REQUIRED_FILES = frozenset(
    {
        ".copier-answers.yml",
        ".dockerignore",
        ".env.example",
        ".gitignore",
        ".pre-commit-config.yaml",
        "AGENTS.md",
        "Dockerfile",
        "Makefile",
        "README.md",
        "SERVICE.md",
        "alembic.ini",
        "pyproject.toml",
        "scripts/check_documentation.py",
    },
)
REQUIRED_DIRECTORIES = frozenset(
    {
        "alembic",
        "app",
        "deploy/helm/templateverification",
        "docs",
        "scripts",
    },
)
FORBIDDEN_FILES = frozenset(
    {
        ".python-version",
        ".python_version",
        "docs/ARCHITECTURE.md",
        "docs/SDK.md",
    },
)
SNAPSHOT_IGNORED_DIRECTORIES = frozenset(
    {
        ".git",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".tox",
        ".venv",
        "__pycache__",
        "build",
        "dist",
        "node_modules",
    },
)
SNAPSHOT_IGNORED_SUFFIXES = (".pyc", ".pyo")


class VerificationError(RuntimeError):
    """Report a failed template verification step without a traceback."""


def _parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--copy-only",
        action="store_true",
        help="Stop after Copier copy, generated-tree validation, and documentation checks.",
    )
    return parser.parse_args()


def _require_tool(name: str) -> None:
    executable = shutil.which(name)
    if executable is None:
        raise VerificationError(f"required tool is unavailable on PATH: {name}")
    print(f"[preflight] {name}: {executable}", flush=True)


def _preflight(*, copy_only: bool) -> None:
    required_tools = ("uvx",) if copy_only else ("git", "uv", "uvx", "make")
    errors: list[str] = []
    for name in required_tools:
        try:
            _require_tool(name)
        except VerificationError as exception:
            errors.append(str(exception))

    if copy_only:
        if errors:
            raise VerificationError("; ".join(errors))
        print("[preflight] copy-only mode: dependency checks are skipped", flush=True)
        return

    if errors:
        details = "\n".join(f"- {error}" for error in errors)
        raise VerificationError(f"full verification prerequisites are not satisfied:\n{details}")


def _snapshot_ignore(_directory: str, names: list[str]) -> set[str]:
    ignored = {
        name
        for name in names
        if name in SNAPSHOT_IGNORED_DIRECTORIES or name.endswith(SNAPSHOT_IGNORED_SUFFIXES)
    }
    return ignored


def _run(command: list[str], *, cwd: Path) -> None:
    print(f"[run] ({cwd}) {shlex.join(command)}", flush=True)
    try:
        result = subprocess.run(command, cwd=cwd, check=False)
    except OSError as exception:
        raise VerificationError(
            f"could not execute {shlex.join(command)}: {exception}",
        ) from exception
    if result.returncode != 0:
        raise VerificationError(
            f"command exited with status {result.returncode}: {shlex.join(command)}",
        )


def _copy_template(source: Path, destination: Path) -> None:
    command = [
        "uvx",
        "--from",
        f"copier=={COPIER_VERSION}",
        "copier",
        "copy",
        str(source),
        str(destination),
        "-d",
        f"service_name={SERVICE_NAME}",
    ]
    _run(command, cwd=REPOSITORY_ROOT)


def _validate_generated_tree(generated: Path) -> None:
    errors: list[str] = []

    for relative_path in sorted(REQUIRED_FILES):
        if not (generated / relative_path).is_file():
            errors.append(f"required generated file is missing: {relative_path}")
    for relative_path in sorted(REQUIRED_DIRECTORIES):
        if not (generated / relative_path).is_dir():
            errors.append(f"required generated directory is missing: {relative_path}")

    actual_documents = {
        path.relative_to(generated).as_posix()
        for path in (generated / "docs").rglob("*.md")
        if path.is_file()
    }
    for relative_path in sorted(REQUIRED_DOCUMENTS - actual_documents):
        errors.append(f"required generated documentation is missing: {relative_path}")
    for relative_path in sorted(actual_documents - REQUIRED_DOCUMENTS):
        errors.append(f"unexpected generated documentation page: {relative_path}")

    for relative_path in sorted(FORBIDDEN_FILES):
        if (generated / relative_path).exists():
            errors.append(f"obsolete or forbidden generated file exists: {relative_path}")

    if errors:
        details = "\n".join(f"- {error}" for error in errors)
        raise VerificationError(f"generated tree validation failed:\n{details}")
    print(
        f"[verify] generated tree contains all {len(REQUIRED_DOCUMENTS)} canonical docs pages",
        flush=True,
    )


def _run_documentation_checker(generated: Path) -> None:
    interpreter = Path(sys.executable)
    if not sys.executable or not interpreter.is_file():
        raise VerificationError("cannot locate the current Python interpreter for docs validation")
    _run([str(interpreter), "scripts/check_documentation.py"], cwd=generated)


def _run_full_generated_checks(generated: Path) -> None:
    _run(["uv", "lock"], cwd=generated)
    _run(["git", "init", "--quiet", "--initial-branch=main"], cwd=generated)
    _run(["git", "add", "--all"], cwd=generated)
    _run(["uv", "sync", "--locked"], cwd=generated)
    _run(["uv", "lock", "--check"], cwd=generated)
    _run(["make", "check"], cwd=generated)
    _run(["make", "check-full"], cwd=generated)


def main() -> int:
    """Generate and verify a disposable service, returning a process exit status."""
    arguments = _parse_arguments()
    try:
        _preflight(copy_only=arguments.copy_only)
        with TemporaryDirectory(prefix="service-template-verification-") as temporary_directory:
            temporary_root = Path(temporary_directory)
            source = temporary_root / "source"
            generated = temporary_root / "generated"

            print(f"[snapshot] copying current template to {source}", flush=True)
            shutil.copytree(
                REPOSITORY_ROOT,
                source,
                ignore=_snapshot_ignore,
                symlinks=True,
            )
            _copy_template(source, generated)
            _validate_generated_tree(generated)
            _run_documentation_checker(generated)

            if not arguments.copy_only:
                _run_full_generated_checks(generated)
    except VerificationError as exception:
        print(f"Template verification failed: {exception}", file=sys.stderr)
        return 1

    mode = "copy-only" if arguments.copy_only else "full"
    print(f"Template verification passed ({mode} mode).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
