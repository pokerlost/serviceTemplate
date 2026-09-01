"""Business-operation fingerprint comparison categories."""

from __future__ import annotations

from enum import StrEnum


class FingerprintComparison(StrEnum):
    """Semantic comparison result for one stored business operation."""

    MATCH = "match"
    CONFLICT = "conflict"
