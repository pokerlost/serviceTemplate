#!/usr/bin/env python3
"""Inspect a disposable service rendered from the current Copier template."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

_EXPECTED_SDK_REVISION = "a10cc8872c5de7e0065b3551e96d23fa2e99958f"


def _contract_name(*parts: str) -> str:
    return "".join(parts)


_EXPECTED_PATHS = (
    ".env.example",
    "AGENTS.md",
    "README.md",
    "SERVICE.md",
    "app/api/application.py",
    "app/api/dependencies/authorization.py",
    "app/api/routers/openapi.py",
    "app/api/routers/root.py",
    "app/api/scopes.py",
    "app/application/ports/handler.py",
    "app/application/ports/pokerlost_token_verifier.py",
    "app/configuration/settings.py",
    "deploy/helm/exampleservice/templates/configmap.yaml",
    "deploy/helm/exampleservice/values.yaml",
    "docs/api/body-authorization.md",
    "docs/api/pokerlost-response.md",
    "docs/architecture/inter-service-clients.md",
    "docs/index.md",
    "pyproject.toml",
    "scripts/check_documentation.py",
)

_OBSOLETE_PATHS = (
    "app/api/openapi.py",
    "app/api/routers/openapi_document",
    "app/api/schemas/orm",
    "app/api/schemas/requests",
    "app/api/schemas/responses",
    "app/application/handler.py",
    "app/application/idempotency",
    "app/persistence/database/result_readers",
    "app/persistence/projections",
    "docs/api/application-response.md",
)

_FORBIDDEN_LITERALS = (
    _contract_name("request.", "headers"),
    _contract_name("response.", "headers"),
    _contract_name("Callable[", "[],"),
)

_FORBIDDEN_PYTHON_LITERALS = (
    _contract_name("Head", "er("),
    _contract_name("OAuth2Password", "Bearer"),
    _contract_name("openapi_", "extra"),
    _contract_name("request.", "headers"),
    _contract_name("response.", "headers"),
    _contract_name("security", "Schemes"),
)

_RETIRED_PAYLOAD_DIGEST_TERM = _contract_name("finger", "print")


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
    assertion = re.compile(r"(^|\n)[ \t]*assert[ \t]+")
    for path in destination.rglob("*"):
        if not path.is_file() or path.suffix not in {".md", ".py", ".toml", ".yaml", ".yml"}:
            continue
        source = path.read_text(encoding="utf-8")
        if _RETIRED_PAYLOAD_DIGEST_TERM in source.lower():
            relative_path = path.relative_to(destination)
            raise RuntimeError(f"Rendered {relative_path} contains retired payload-digest code")
        for forbidden in _FORBIDDEN_LITERALS:
            if forbidden in source:
                relative_path = path.relative_to(destination)
                raise RuntimeError(f"Rendered {relative_path} contains forbidden {forbidden}")
        if path.suffix == ".py":
            relative_path = path.relative_to(destination)
            for forbidden in _FORBIDDEN_PYTHON_LITERALS:
                if forbidden in source:
                    raise RuntimeError(f"Rendered {relative_path} contains forbidden {forbidden}")
            if assertion.search(source) is not None:
                raise RuntimeError(f"Rendered {relative_path} contains a runtime assertion")


def _check_rendered_contract(destination: Path) -> None:
    for relative_path in _EXPECTED_PATHS:
        if not (destination / relative_path).is_file():
            raise RuntimeError(f"Rendered template is missing {relative_path}")
    for relative_path in _OBSOLETE_PATHS:
        if (destination / relative_path).exists():
            raise RuntimeError(f"Rendered template retains obsolete {relative_path}")
    router_directories = tuple(
        path
        for path in (destination / "app/api/routers").iterdir()
        if path.is_dir() and path.name != "__pycache__"
    )
    if router_directories:
        rendered = ", ".join(
            str(path.relative_to(destination)) for path in sorted(router_directories)
        )
        raise RuntimeError(f"Rendered template contains nested router directories: {rendered}")

    environment = _read_required_file(destination, ".env.example")
    _require_source(
        environment,
        (
            "EXAMPLESERVICE_ROOT_OPERATION=getRoot",
            "EXAMPLESERVICE_OPENAPI_OPERATION=getOpenApi",
        ),
        label=".env.example",
    )

    settings = _read_required_file(destination, "app/configuration/settings.py")
    _require_source(
        settings,
        (
            "root_operation: PokerlostOperation",
            "openapi_operation: PokerlostOperation",
        ),
        label="Settings",
    )

    root_router = _read_required_file(destination, "app/api/routers/root.py")
    _require_source(
        root_router,
        (
            "def create_root_router(*, operation: PokerlostOperation) -> APIRouter:",
            "@router.get(",
            'path="/"',
            "operation_id=operation",
            "response_model=PokerlostResponse[None]",
            "async def get_service_root() -> PokerlostResponse[None]:",
        ),
        label="root router",
    )

    openapi_router = _read_required_file(destination, "app/api/routers/openapi.py")
    _require_source(
        openapi_router,
        (
            "def create_openapi_router(",
            "operation: PokerlostOperation",
            "@router.get(",
            'path=f"/{operation}"',
            "operation_id=operation",
            "response_model=PokerlostResponse[dict[str, JSONValue]]",
            "application.openapi()",
        ),
        label="OpenAPI router",
    )

    routes = _read_required_file(destination, "app/api/routes.py")
    _require_source(
        routes,
        (
            "create_root_router(",
            "operation=settings.root_operation",
            "create_openapi_router(",
            "application=application",
            "operation=settings.openapi_operation",
        ),
        label="route composition",
    )

    application = _read_required_file(destination, "app/api/application.py")
    resources = _read_required_file(destination, "app/api/resources.py")
    _require_source(
        application,
        (
            "token_verifier: PokerlostTokenVerifier | None = None",
            "token_verifier=token_verifier",
        ),
        label="application composition",
    )
    _require_source(
        resources,
        ("token_verifier: PokerlostTokenVerifier | None",),
        label="application resources",
    )

    verifier = _read_required_file(
        destination,
        "app/application/ports/pokerlost_token_verifier.py",
    )
    _require_source(
        verifier,
        (
            "class PokerlostTokenVerifier(Protocol):",
            "async def verify(",
            "token: str",
            "audience: str",
            ") -> PokerlostAuthorizationContext:",
        ),
        label="token verifier port",
    )

    scopes = _read_required_file(destination, "app/api/scopes.py")
    _require_source(scopes, ("class Scope(StrEnum):", "PokerlostScope(value)"), label="scopes")

    authorization = _read_required_file(destination, "app/api/dependencies/authorization.py")
    _require_source(
        authorization,
        (
            "await request.json()",
            'body.get("authorization")',
            "PokerlostAuthorization.model_validate",
            "await verifier.verify(",
            "authorization.access_token",
            "context.audience != SERVICE_NAME",
            "security_scopes.scopes",
            "scope not in granted_scopes",
        ),
        label="body authorization dependency",
    )
    for forbidden in ("role", "httpx", "auth_service", "request.body("):
        if forbidden in authorization:
            raise RuntimeError(
                f"Rendered body authorization dependency contains forbidden {forbidden}"
            )

    request_context = _read_required_file(destination, "app/api/request_context.py")
    _require_source(
        request_context,
        ("request_id = str(uuid4())", "request.state.request_id = request_id"),
        label="request context",
    )

    handler = _read_required_file(destination, "app/application/ports/handler.py")
    _require_source(
        handler,
        ("from typing import Protocol", "class Handler[", "](Protocol):", "async def __call__("),
        label="Handler port",
    )

    values = _read_required_file(destination, "deploy/helm/exampleservice/values.yaml")
    _require_source(
        values,
        (
            "rootOperation: getRoot",
            "openapiOperation: getOpenApi",
            "mandatory deployment HTTPS/TLS termination",
        ),
        label="Helm values",
    )

    configmap = _read_required_file(
        destination,
        "deploy/helm/exampleservice/templates/configmap.yaml",
    )
    _require_source(
        configmap,
        ("EXAMPLESERVICE_ROOT_OPERATION:", "EXAMPLESERVICE_OPENAPI_OPERATION:"),
        label="ConfigMap",
    )

    pristine_sources = (
        ("app/api/resources.py", resources),
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
            "Mapping[str, PokerlostClient]",
            "token_cache",
            "token_refresh",
            "FakeTokenVerifier",
        ):
            if forbidden in source:
                raise RuntimeError(
                    f"Rendered pristine {relative_path} contains placeholder {forbidden}"
                )

    agents = _read_required_file(destination, "AGENTS.md")
    _require_source(
        agents,
        (
            "private body-only JSON protocol",
            "PokerlostRetryPolicy",
            "PokerlostRequestOptions(retry_policy=PokerlostRetryPolicy())",
            "Pokerlost scopes use dot-separated lowerCamelCase segments",
            "Security(authorize_pokerlost_request, scopes=[...])",
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
            "PokerlostAuthorizationMiddleware",
            "PokerlostRetryMiddleware",
            "PokerlostRetryPolicy",
            "getToken",
            "refreshToken",
            "retry_after",
            "Do not instantiate an authService",
        ),
        label="inter-service client guidance",
    )

    documentation_index = _read_required_file(destination, "docs/index.md")
    for page in (
        "`docs/api/body-authorization.md`",
        "`docs/api/pokerlost-response.md`",
        "`docs/architecture/inter-service-clients.md`",
    ):
        if page not in documentation_index:
            raise RuntimeError(f"Rendered docs index omits {page}")

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
