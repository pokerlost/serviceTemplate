"""Service-owned exact Pokerlost scope catalog."""

from __future__ import annotations

from enum import StrEnum

from pypokerlost.types import PokerlostScope


class Scope(StrEnum):
    """Empty pristine catalog; concrete services add only implemented exact scopes."""

    def __new__(cls, value: str) -> Scope:
        """Validate every concrete catalog member through PokerlostScope."""
        validated = str(PokerlostScope(value))
        member = str.__new__(cls, validated)
        member._value_ = validated
        return member
