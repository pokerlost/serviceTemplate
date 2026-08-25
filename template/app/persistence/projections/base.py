"""Transport-independent read projection contract."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Self


class Projection(ABC):
    """Typed application-facing result of a persistence read query."""

    @classmethod
    @abstractmethod
    def from_mapping(cls, values: Mapping[str, object]) -> Self:
        """Build a projection from explicitly labeled query values."""
