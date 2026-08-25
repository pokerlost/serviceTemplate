"""Small Typer interface for local service startup."""

from __future__ import annotations

from typing import Annotated

import typer
import uvicorn

from configuration import Settings
from service import SERVICE_NAME, SERVICE_SLUG

cli = typer.Typer(
    name=SERVICE_SLUG,
    help=f"Run the {SERVICE_NAME} service locally.",
    no_args_is_help=True,
)


@cli.callback()
def operator_cli() -> None:
    """Expose development and service-owned operator commands."""


@cli.command()
def run(
    host: Annotated[
        str | None,
        typer.Option(help="HTTP bind host override."),
    ] = None,
    port: Annotated[
        int | None,
        typer.Option(min=1, max=65535, help="HTTP bind port override."),
    ] = None,
    reload: Annotated[
        bool,
        typer.Option(help="Reload the local server when source files change."),
    ] = False,
) -> None:
    """Start one local Uvicorn development worker."""
    settings = Settings()
    uvicorn.run(
        "api.application:create_app",
        factory=True,
        host=host if host is not None else settings.http.host,
        port=port if port is not None else settings.http.port,
        workers=1,
        reload=reload,
        access_log=False,
    )
