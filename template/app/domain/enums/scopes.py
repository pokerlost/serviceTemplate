"""Service-owned exact Pokerlost scope catalog."""

from __future__ import annotations

import re
from enum import StrEnum, unique

_SCOPE_PATTERN = re.compile(r"^[a-z][A-Za-z0-9]*(?:\.[a-z][A-Za-z0-9]*)+$")


@unique
class Scopes(StrEnum):
    """Empty pristine catalog; concrete services add implemented capabilities."""

    def __new__(cls, value: str) -> Scopes:
        """Reject values outside the stable dotted lowerCamelCase contract."""
        if _SCOPE_PATTERN.fullmatch(value) is None:
            raise ValueError("Pokerlost scopes must contain dotted lowerCamelCase segments")
        member = str.__new__(cls, value)
        member._value_ = value
        return member


_SCOPE_DESCRIPTIONS: dict[Scopes, str] = {}


def scope_descriptions() -> dict[str, str]:
    """Return the complete OpenAPI description catalog for local scopes."""
    described_scopes = frozenset(_SCOPE_DESCRIPTIONS)
    declared_scopes = frozenset(Scopes)
    if described_scopes != declared_scopes:
        raise RuntimeError("Every local Pokerlost scope must have exactly one description")
    if any(not description.strip() for description in _SCOPE_DESCRIPTIONS.values()):
        raise RuntimeError("Pokerlost scope descriptions must not be empty")
    return {scope.value: description for scope, description in _SCOPE_DESCRIPTIONS.items()}
