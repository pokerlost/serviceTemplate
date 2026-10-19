"""Service-owned exact scope catalog, preserved during template updates."""

from __future__ import annotations

import re
from enum import StrEnum, unique

_SCOPE_PATTERN = re.compile(r"^[a-z][A-Za-z0-9]*(?:\.[a-z][A-Za-z0-9]*)+$")


@unique
class Scopes(StrEnum):
    """Add only implemented service capabilities with exact descriptions."""

    def __new__(cls, value: str) -> Scopes:
        if _SCOPE_PATTERN.fullmatch(value) is None:
            raise ValueError(
                "Scopes require dotted lower camelCase capability segments"
            )
        member = str.__new__(cls, value)
        member._value_ = value
        return member


SCOPE_DESCRIPTIONS: dict[Scopes, str] = {}


def scope_descriptions() -> dict[str, str]:
    if frozenset(SCOPE_DESCRIPTIONS) != frozenset(Scopes):
        raise RuntimeError("Every declared scope needs one description")
    if any(not value.strip() for value in SCOPE_DESCRIPTIONS.values()):
        raise RuntimeError("Scope descriptions must not be empty")
    return {
        scope.value: description for scope, description in SCOPE_DESCRIPTIONS.items()
    }
