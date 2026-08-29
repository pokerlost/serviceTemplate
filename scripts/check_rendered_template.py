#!/usr/bin/env python3
"""Inspect a disposable service rendered from the current Copier template."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

_EXPECTED_PATHS = (
    ".env.example",
    "AGENTS.md",
    "README.md",
    "SERVICE.md",
    "app/api/application.py",
    "app/api/routers/openapi_document/router.py",
    "app/api/routers/root.py",
    "app/application/idempotency/business_operation_fingerprinting.py",
    "app/configuration/business_operation_fingerprint.py",
    "app/configuration/settings.py",
    "deploy/helm/exampleservice/templates/configmap.yaml",
    "deploy/helm/exampleservice/values.yaml",
    "docs/index.md",
    "pyproject.toml",
    "scripts/check_documentation.py",
)


def _read_required_file(destination: Path, relative_path: str) -> str:
    path = destination / relative_path
    if not path.is_file():
        raise RuntimeError(f"Rendered template is missing {relative_path}")
    return path.read_text(encoding="utf-8")


def _check_rendered_contract(destination: Path) -> None:
    for relative_path in _EXPECTED_PATHS:
        if not (destination / relative_path).is_file():
            raise RuntimeError(f"Rendered template is missing {relative_path}")

    environment = _read_required_file(destination, ".env.example")
    for expected in (
        "EXAMPLESERVICE_ROOT_OPERATION=exampleservice.getRoot",
        "EXAMPLESERVICE_OPENAPI_OPERATION=openapi.get",
        "EXAMPLESERVICE_BUSINESS_OPERATION_FINGERPRINT__KEY_VERSION=1",
    ):
        if expected not in environment:
            raise RuntimeError(f"Rendered .env.example is missing {expected}")

    settings = _read_required_file(destination, "app/configuration/settings.py")
    if "root_operation: APIOperation" not in settings:
        raise RuntimeError("Rendered Settings does not type root_operation as APIOperation")
    if "openapi_operation: APIOperation" not in settings:
        raise RuntimeError("Rendered Settings does not type openapi_operation as APIOperation")

    root_router = _read_required_file(destination, "app/api/routers/root.py")
    if 'path="/"' not in root_router or "operation_id=settings.root_operation" not in root_router:
        raise RuntimeError("Rendered root route is not settings-driven")

    openapi_router = _read_required_file(
        destination,
        "app/api/routers/openapi_document/router.py",
    )
    if 'path=f"/{settings.openapi_operation}"' not in openapi_router:
        raise RuntimeError("Rendered OpenAPI path is not settings-driven")
    if "operation_id=settings.openapi_operation" not in openapi_router:
        raise RuntimeError("Rendered OpenAPI operation ID is not settings-driven")

    fingerprinting = _read_required_file(
        destination,
        "app/application/idempotency/business_operation_fingerprinting.py",
    )
    for required_source in (
        "hmac.compare_digest",
        "digestmod=sha256",
        "def _encode_field_name",
        "def _encode_field_value",
    ):
        if required_source not in fingerprinting:
            raise RuntimeError(f"Rendered fingerprinting source is missing {required_source}")
    if "@staticmethod" in fingerprinting:
        raise RuntimeError("Rendered fingerprinting source contains a static method")

    values = _read_required_file(destination, "deploy/helm/exampleservice/values.yaml")
    if "rootOperation: exampleservice.getRoot" not in values:
        raise RuntimeError("Rendered Helm values are missing rootOperation")
    if "openapiOperation: openapi.get" not in values:
        raise RuntimeError("Rendered Helm values are missing openapiOperation")

    configmap = _read_required_file(
        destination,
        "deploy/helm/exampleservice/templates/configmap.yaml",
    )
    for expected in (
        "EXAMPLESERVICE_ROOT_OPERATION:",
        "EXAMPLESERVICE_OPENAPI_OPERATION:",
    ):
        if expected not in configmap:
            raise RuntimeError(f"Rendered ConfigMap is missing {expected}")
    if "EXAMPLESERVICE_BUSINESS_OPERATION_FINGERPRINT__SECRET" in configmap:
        raise RuntimeError("Rendered ConfigMap exposes the fingerprint secret")

    project = _read_required_file(destination, "pyproject.toml")
    if "8ca9d7153a99f57149364e0b860c319b02cac602" not in project:
        raise RuntimeError("Rendered project does not pin the final pypokerlost revision")


def _run_static_checks(destination: Path) -> None:
    commands = (
        [sys.executable, "scripts/check_documentation.py"],
        [sys.executable, "-m", "compileall", "-q", "app", "alembic/env.py", "scripts"],
    )
    for command in commands:
        subprocess.run(command, cwd=destination, check=True)


def _parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("copy", "check"))
    parser.add_argument("destination", type=Path)
    return parser.parse_args()


def main() -> int:
    """Validate one rendered destination and optionally run its static checks."""
    arguments = _parse_arguments()
    destination = arguments.destination.resolve()
    if not destination.is_dir():
        raise RuntimeError(f"Rendered destination does not exist: {destination}")

    _check_rendered_contract(destination)
    if arguments.mode == "check":
        _run_static_checks(destination)
    print(f"Template {arguments.mode} verification passed for a disposable render.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
