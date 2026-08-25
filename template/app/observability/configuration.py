"""Privacy-safe Pydantic Logfire configuration."""

from __future__ import annotations

from typing import Literal

import logfire

from configuration import Settings
from service import SERVICE_NAME


def configure_observability(settings: Settings) -> None:
    """Configure the process-wide Logfire SDK once at composition time."""
    logfire_settings = settings.logfire

    console: logfire.ConsoleOptions | Literal[False]
    if logfire_settings.enabled and logfire_settings.console:
        console = logfire.ConsoleOptions(
            min_log_level=logfire_settings.minimum_level,
        )
    else:
        console = False

    token = (
        logfire_settings.token.get_secret_value()
        if logfire_settings.enabled
        and logfire_settings.send_to_logfire
        and logfire_settings.token is not None
        else None
    )
    logfire.configure(
        service_name=SERVICE_NAME,
        service_version=settings.application.version,
        environment=settings.application.environment.value,
        send_to_logfire=(logfire_settings.send_to_logfire if logfire_settings.enabled else False),
        token=token,
        console=console,
        inspect_arguments=False,
        min_level=logfire_settings.minimum_level,
        scrubbing=logfire.ScrubbingOptions(
            extra_patterns=(
                "authorization",
                "cookie",
                "credential",
                "database[._ -]?url",
                "dsn",
                "password",
                "private[._ -]?key",
                "secret",
                "token",
            ),
        ),
    )
