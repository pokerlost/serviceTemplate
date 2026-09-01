"""FastAPI application factory and composition root."""

from __future__ import annotations

from fastapi import FastAPI

from application.ports import PokerlostTokenVerifier
from configuration import Settings
from observability import configure_observability, instrument_fastapi
from service import SERVICE_NAME

from .errors import configure_exception_handlers
from .lifespan import create_lifespan
from .request_context import configure_request_context
from .routes import configure_routes


def create_app(
    settings: Settings | None = None,
    *,
    token_verifier: PokerlostTokenVerifier | None = None,
) -> FastAPI:
    """Build a configured service without creating import-time resources."""
    resolved_settings = settings if settings is not None else Settings()
    configure_observability(resolved_settings)
    application = FastAPI(
        title=SERVICE_NAME,
        version=resolved_settings.application.version,
        debug=False,
        lifespan=create_lifespan(
            resolved_settings,
            token_verifier=token_verifier,
        ),
        openapi_url=None,
        docs_url=None,
        redoc_url=None,
    )

    configure_request_context(application)
    configure_exception_handlers(application)
    configure_routes(application, resolved_settings)
    instrument_fastapi(application, resolved_settings)
    return application
