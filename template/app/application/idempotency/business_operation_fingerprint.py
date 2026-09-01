"""Persistable business-operation fingerprint value."""

from __future__ import annotations

import hmac
from typing import Self

from pydantic import Field

from domain.value_model import ValueModel

from .enums import FingerprintComparison


class BusinessOperationFingerprint(ValueModel):
    """Persistable keyed digest and the key version that produced it."""

    digest: bytes = Field(
        min_length=32,
        max_length=32,
        repr=False,
    )
    key_version: int = Field(ge=1)

    def compare(
        self,
        candidate: Self,
    ) -> FingerprintComparison:
        """Compare one candidate digest in constant time."""
        digest_matches = hmac.compare_digest(
            self.digest,
            candidate.digest,
        )
        key_version_matches = self.key_version == candidate.key_version
        if digest_matches and key_version_matches:
            return FingerprintComparison.MATCH
        return FingerprintComparison.CONFLICT
