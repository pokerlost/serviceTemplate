"""Central exception handler registration."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

from application.errors import ApplicationError

from .application import handle_application_error
from .database import (
    DatabaseUnavailableError,
    handle_database_error,
    handle_database_unavailable,
)
from .http import handle_http_error
from .validation import handle_validation_error


def configure_exception_handlers(application: FastAPI) -> None:
    """Register sanitized handlers from specific to general."""
    application.add_exception_handler(ApplicationError, handle_application_error)
    application.add_exception_handler(
        DatabaseUnavailableError,
        handle_database_unavailable,
    )
    application.add_exception_handler(SQLAlchemyError, handle_database_error)
    application.add_exception_handler(RequestValidationError, handle_validation_error)
    application.add_exception_handler(StarletteHTTPException, handle_http_error)
