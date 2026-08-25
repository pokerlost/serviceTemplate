"""Application output base."""

from __future__ import annotations

from abc import ABC, abstractmethod


class Result(ABC):
    """Marker base for typed application output."""
