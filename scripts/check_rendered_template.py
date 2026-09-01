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
    "docs/architecture/inter-service-clients.md",
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

    resources = _read_required_file(destination, "app/api/resources.py")
    lifespan = _read_required_file(destination, "app/api/lifespan.py")
    for relative_path, source in (
        ("app/api/resources.py", resources),
        ("app/api/lifespan.py", lifespan),
        ("app/configuration/settings.py", settings),
        (".env.example", environment),
    ):
        for forbidden_source in (
            "AuthServiceSettings",
            "ClientCredentialsTokenProvider",
            "RetryMiddleware",
            "auth_service_client",
            "AUTH_SERVICE__CLIENT_SECRET",
            "Mapping[str, Client]",
        ):
            if forbidden_source in source:
                raise RuntimeError(
                    f"Rendered pristine {relative_path} contains placeholder {forbidden_source}"
                )

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

    agents = _read_required_file(destination, "AGENTS.md")
    for expected in (
        "one target-specific `pypokerlost.Client`",
        "ClientCredentialsTokenProvider",
        "`RetryMiddleware()` outermost",
        "`RequestOptions(retry=RetryPolicy(...))`",
        "same `business_operation_id` and the same semantic payload",
        "PostgreSQL transaction open across token acquisition",
        "Do not automatically replay `401` or `403`",
        "Do not add a placeholder client",
    ):
        if expected not in agents:
            raise RuntimeError(f"Rendered AGENTS.md is missing outbound rule {expected}")

    inter_service_clients = _read_required_file(
        destination,
        "docs/architecture/inter-service-clients.md",
    )
    for expected in (
        "from pypokerlost.client.auth import ClientCredentials, ClientCredentialsTokenProvider",
        "from pypokerlost.client.retry import RetryPolicy",
        "from pypokerlost.middleware import BearerTokenMiddleware, RetryMiddleware",
        "middleware=(",
        "RetryMiddleware(),",
        "BearerTokenMiddleware(token_provider),",
        "options=RequestOptions(retry=retry_policy)",
        "type AuthServiceClient = Annotated[",
        "def create_lifespan(settings: Settings) -> ApplicationLifespan:",
        "from observability import instrument_database",
        "from .auth_service_client import create_auth_service_client",
        "total_budget_seconds: float | None = Field(",
        "respect_retry_after: bool = True",
        "do not put `Field(strict=True)` on scalar fields that",
        "EXAMPLESERVICE_AUTH_SERVICE__CLIENT_SECRET",
        "does not instantiate a client or require outbound credentials",
    ):
        if expected not in inter_service_clients:
            raise RuntimeError(f"Rendered inter-service client guidance is missing {expected}")

    for forbidden in (
        "max_attempts: int = Field(default=3, strict=True",
        "initial_delay_seconds: float = Field(default=0.2, strict=True",
        "max_delay_seconds: float = Field(default=2.0, strict=True",
        "backoff_multiplier: float = Field(default=2.0, strict=True",
        "\n        strict=True,\n",
        "respect_retry_after: bool = Field(default=True, strict=True)",
        "token_refresh_skew_seconds: float = Field(default=30.0, strict=True",
        "request_timeout_seconds: int = Field(default=10, strict=True",
    ):
        if forbidden in inter_service_clients:
            raise RuntimeError("Rendered inter-service settings reject environment-string inputs")

    documentation_index = _read_required_file(destination, "docs/index.md")
    if "`docs/architecture/inter-service-clients.md`" not in documentation_index:
        raise RuntimeError("Rendered docs index omits inter-service client guidance")

    for relative_path, source in (
        ("deploy/helm/exampleservice/templates/configmap.yaml", configmap),
        ("deploy/helm/exampleservice/values.yaml", values),
    ):
        if "AUTH_SERVICE" in source or "CLIENT_SECRET" in source:
            raise RuntimeError(f"Rendered pristine {relative_path} contains outbound credentials")

    project = _read_required_file(destination, "pyproject.toml")
    if "8ca9d7153a99f57149364e0b860c319b02cac602" not in project:
        raise RuntimeError("Rendered project does not pin the current reachable SDK revision")


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
