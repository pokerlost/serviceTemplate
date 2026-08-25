"""Shared public API model facade."""

from __future__ import annotations

from .request_model import RequestModel
from .response_model import ResponseModel

__all__ = ("RequestModel", "ResponseModel")
