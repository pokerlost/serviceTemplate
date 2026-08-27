"""JSON-compatible public API value types."""

from __future__ import annotations

from pydantic import FiniteFloat

type JSONScalar = bool | int | FiniteFloat | str | None
type JSONValue = JSONScalar | list[JSONValue] | dict[str, JSONValue]
