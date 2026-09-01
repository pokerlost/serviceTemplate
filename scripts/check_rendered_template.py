#!/usr/bin/env python3
"""Inspect a disposable service rendered from the current Copier template."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

_EXPECTED_SDK_REVISION = "f2de9e11e66c52685d7324b0d70d747358a8d6e1"


def _contract_name(*parts: str) -> str:
    return "".join(parts)


_EXPECTED_PATHS = (
    ".env.example",
    "AGENTS.md",
    "README.md",
    "SERVICE.md",
    "app/api/application.py",
    "app/api/routers/openapi_document/router.py",
    "app/api/routers/root.py",
    "app/application/idempotency/business_operation_fingerprint.py",
    "app/application/idempotency/business_operation_fingerprinter.py",
    "app/application/idempotency/constants.py",
    "app/application/idempotency/enums.py",
    "app/application/idempotency/types.py",
    "app/application/ports/handler.py",
    "app/configuration/business_operation_fingerprint.py",
    "app/configuration/settings.py",
    "deploy/helm/exampleservice/templates/configmap.yaml",
    "deploy/helm/exampleservice/values.yaml",
    "docs/architecture/inter-service-clients.md",
    "docs/index.md",
    "pyproject.toml",
    "scripts/check_documentation.py",
)

_OBSOLETE_PATHS = (
    "app/application/handler.py",
    _contract_name(
        "app/application/idempotency/business_operation_",
        "fingerprinting.py",
    ),
)


def _read_required_file(destination: Path, relative_path: str) -> str:
    path = destination / relative_path
    if not path.is_file():
        raise RuntimeError(f"Rendered template is missing {relative_path}")
    return path.read_text(encoding="utf-8")


def _require_source(source: str, expected: tuple[str, ...], *, label: str) -> None:
    for fragment in expected:
        if fragment not in source:
            raise RuntimeError(f"Rendered {label} is missing {fragment}")


def _check_forbidden_contracts(destination: Path) -> None:
    forbidden_literals = (
        _contract_name("AccessToken", "Provider"),
        _contract_name("BearerToken", "Middleware"),
        _contract_name("ClientCredentialsToken", "Provider"),
        _contract_name("Retry", "Middleware"),
        _contract_name("APIClientRetry", "Settings"),
        _contract_name("TokenRetry", "Settings"),
        _contract_name("OperationRetry", "Settings"),
        _contract_name("add_api_", "route("),
        _contract_name("openapi_", "extra="),
        _contract_name("pokerlost.business-operation-", "fingerprint.v1"),
        _contract_name("auth.internal.provision", "_human"),
    )
    operation_constant = re.compile(r"\b[A-Z_]*OPERATION\s*:\s*Final\s*\[\s*APIOperation\s*\]")
    old_retry_policy = re.compile(_contract_name(r"(?<!PokerLost)\bRetry", r"Policy\b"))

    for path in destination.rglob("*"):
        if not path.is_file() or path.suffix not in {".md", ".py", ".toml", ".yaml", ".yml"}:
            continue
        source = path.read_text(encoding="utf-8")
        for forbidden in forbidden_literals:
            if forbidden in source:
                relative_path = path.relative_to(destination)
                raise RuntimeError(f"Rendered {relative_path} contains forbidden {forbidden}")
        if operation_constant.search(source) is not None:
            relative_path = path.relative_to(destination)
            raise RuntimeError(f"Rendered {relative_path} contains a route operation constant")
        if old_retry_policy.search(source) is not None:
            relative_path = path.relative_to(destination)
            raise RuntimeError(f"Rendered {relative_path} contains the obsolete retry policy")


def _check_rendered_contract(destination: Path) -> None:
    for relative_path in _EXPECTED_PATHS:
        if not (destination / relative_path).is_file():
            raise RuntimeError(f"Rendered template is missing {relative_path}")
    for relative_path in _OBSOLETE_PATHS:
        if (destination / relative_path).exists():
            raise RuntimeError(f"Rendered template retains obsolete {relative_path}")

    environment = _read_required_file(destination, ".env.example")
    _require_source(
        environment,
        (
            "EXAMPLESERVICE_ROOT_OPERATION=exampleservice.getRoot",
            "EXAMPLESERVICE_OPENAPI_OPERATION=openapi.get",
            "EXAMPLESERVICE_BUSINESS_OPERATION_FINGERPRINT__KEY_VERSION=1",
        ),
        label=".env.example",
    )

    settings = _read_required_file(destination, "app/configuration/settings.py")
    _require_source(
        settings,
        (
            "root_operation: APIOperation",
            "openapi_operation: APIOperation",
        ),
        label="Settings",
    )

    root_router = _read_required_file(destination, "app/api/routers/root.py")
    _require_source(
        root_router,
        (
            "def create_root_router(*, operation: APIOperation) -> APIRouter:",
            "@router.get(",
            'path="/"',
            "operation_id=operation",
            "async def get_service_root() -> RootResponse:",
        ),
        label="root router",
    )

    openapi_router = _read_required_file(
        destination,
        "app/api/routers/openapi_document/router.py",
    )
    _require_source(
        openapi_router,
        (
            "def create_openapi_document_router(",
            "application: FastAPI",
            "operation: APIOperation",
            "@router.get(",
            'path=f"/{operation}"',
            "operation_id=operation",
            "async def get_openapi_document() -> OpenAPIResponse:",
            "result=application.openapi()",
        ),
        label="OpenAPI router",
    )

    routes = _read_required_file(destination, "app/api/routes.py")
    _require_source(
        routes,
        (
            "create_root_router(",
            "operation=settings.root_operation",
            "create_openapi_document_router(",
            "application=application",
            "operation=settings.openapi_operation",
        ),
        label="route composition",
    )

    handler = _read_required_file(destination, "app/application/ports/handler.py")
    _require_source(
        handler,
        (
            "from typing import Protocol",
            "class Handler[",
            "](Protocol):",
            "async def __call__(",
        ),
        label="Handler port",
    )

    constants = _read_required_file(destination, "app/application/idempotency/constants.py")
    _require_source(
        constants,
        (
            'b"pokerlost.businessOperationFingerprint.v2\\x00"',
            'r"[a-z][A-Za-z0-9]*"',
            "MAX_FIELD_COUNT: Final[int] = 65_535",
            "MAX_FIELD_NAME_BYTES: Final[int] = 65_535",
        ),
        label="fingerprint constants",
    )

    fingerprint = _read_required_file(
        destination,
        "app/application/idempotency/business_operation_fingerprint.py",
    )
    fingerprinter = _read_required_file(
        destination,
        "app/application/idempotency/business_operation_fingerprinter.py",
    )
    _require_source(
        fingerprint,
        (
            "hmac.compare_digest",
            "def compare(",
        ),
        label="fingerprint value",
    )
    _require_source(
        fingerprinter,
        (
            "digestmod=sha256",
            "def _encode_field_name",
            "def _encode_field_value",
        ),
        label="fingerprinter",
    )
    if "@staticmethod" in fingerprint or "@staticmethod" in fingerprinter:
        raise RuntimeError("Rendered fingerprint package contains a static method")

    values = _read_required_file(destination, "deploy/helm/exampleservice/values.yaml")
    _require_source(
        values,
        (
            "rootOperation: exampleservice.getRoot",
            "openapiOperation: openapi.get",
        ),
        label="Helm values",
    )

    configmap = _read_required_file(
        destination,
        "deploy/helm/exampleservice/templates/configmap.yaml",
    )
    _require_source(
        configmap,
        (
            "EXAMPLESERVICE_ROOT_OPERATION:",
            "EXAMPLESERVICE_OPENAPI_OPERATION:",
        ),
        label="ConfigMap",
    )
    if "EXAMPLESERVICE_BUSINESS_OPERATION_FINGERPRINT__SECRET" in configmap:
        raise RuntimeError("Rendered ConfigMap exposes the fingerprint secret")

    pristine_sources = (
        ("app/api/resources.py", _read_required_file(destination, "app/api/resources.py")),
        ("app/api/lifespan.py", _read_required_file(destination, "app/api/lifespan.py")),
        ("app/configuration/settings.py", settings),
        (".env.example", environment),
        ("deploy/helm/exampleservice/templates/configmap.yaml", configmap),
        ("deploy/helm/exampleservice/values.yaml", values),
    )
    for relative_path, source in pristine_sources:
        for forbidden in (
            "AuthServiceSettings",
            "auth_service_client",
            "AUTH_SERVICE__CLIENT_SECRET",
            "Mapping[str, Client]",
            _contract_name(
                "token_",
                "cache",
            ),
            "token_refresh",
        ):
            if forbidden in source:
                raise RuntimeError(
                    f"Rendered pristine {relative_path} contains placeholder {forbidden}"
                )

    agents = _read_required_file(destination, "AGENTS.md")
    _require_source(
        agents,
        (
            "service-owned application port",
            "`PokerLostRetryPolicy`",
            "`RequestOptions(retry=PokerLostRetryPolicy())`",
            "OAuth scopes use at least two dot-separated lowerCamelCase segments",
            "functional `create_<feature>_router(...)` factory",
            "structural asynchronous",
            "`Handler` Protocol",
            "pokerlost.businessOperationFingerprint.v2",
            "`business_operation_id`, semantic payload, and target operation",
            "Do not automatically replay `401` or `403`",
        ),
        label="AGENTS.md",
    )

    inter_service_clients = _read_required_file(
        destination,
        "docs/architecture/inter-service-clients.md",
    )
    _require_source(
        inter_service_clients,
        (
            "service-owned application port",
            "service-owned pypokerlost adapter",
            "generated oauth.token method",
            "from pypokerlost.client.retry import PokerLostRetryPolicy",
            "retry=PokerLostRetryPolicy()",
            "application/x-www-form-urlencoded",
            "auth.internal.provisionHuman",
            "do not acquire, cache, refresh, sign, verify, or revoke tokens",
            "Do not instantiate an authService client",
        ),
        label="inter-service client guidance",
    )

    documentation_index = _read_required_file(destination, "docs/index.md")
    if "`docs/architecture/inter-service-clients.md`" not in documentation_index:
        raise RuntimeError("Rendered docs index omits inter-service client guidance")

    project = _read_required_file(destination, "pyproject.toml")
    sdk_source = re.search(
        r'pypokerlost = \{ git = "ssh://git@github\.com/pokerlost/pypokerlost\.git", '
        r'rev = "([0-9a-f]{40})" \}',
        project,
    )
    if sdk_source is None:
        raise RuntimeError("Rendered project does not pin one full SDK Git revision")
    if sdk_source.group(1) != _EXPECTED_SDK_REVISION:
        raise RuntimeError("Rendered project does not pin the verified SDK revision")

    _check_forbidden_contracts(destination)


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
