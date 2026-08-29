"""Keyed deterministic fingerprints for resumable business operations."""

from __future__ import annotations

import hmac
import re
from collections.abc import Mapping
from enum import StrEnum
from hashlib import sha256
from typing import Final, Self

from pydantic import Field, SecretStr

from domain.value_model import ValueModel

_CANONICAL_FORMAT_DOMAIN: Final = b"pokerlost.business-operation-fingerprint.v1\x00"
_FIELD_NAME_PATTERN: Final = re.compile(r"[a-z][a-z0-9_]*", flags=re.ASCII)
_MAX_FIELD_COUNT: Final = 65_535
_MAX_FIELD_NAME_BYTES: Final = 65_535

type FingerprintFieldValue = str | bytes


class FingerprintComparison(StrEnum):
    """Semantic comparison result for one stored business operation."""

    MATCH = "match"
    CONFLICT = "conflict"


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


class BusinessOperationFingerprinter:
    """Create keyed digests without retaining canonical plaintext."""

    __slots__ = ("_key_version", "_secret")

    def __init__(
        self,
        secret: SecretStr,
        *,
        key_version: int,
    ) -> None:
        """Store one dedicated secret and positive key version."""
        secret_bytes = secret.get_secret_value().encode("utf-8")
        if len(secret_bytes) < 32:
            raise ValueError(
                "Business-operation fingerprint secret must contain at least 32 UTF-8 bytes"
            )
        if key_version < 1:
            raise ValueError("Business-operation fingerprint key version must be positive")
        self._secret = secret_bytes
        self._key_version = key_version

    def fingerprint(
        self,
        fields: Mapping[str, FingerprintFieldValue],
    ) -> BusinessOperationFingerprint:
        """Hash named exact values in deterministic field-name order."""
        if not fields or len(fields) > _MAX_FIELD_COUNT:
            raise ValueError("Business-operation fingerprint fields are invalid")

        digest = hmac.new(
            self._secret,
            digestmod=sha256,
        )
        digest.update(_CANONICAL_FORMAT_DOMAIN)
        digest.update(
            len(fields).to_bytes(
                2,
                byteorder="big",
            ),
        )

        for field_name in sorted(fields):
            name_bytes = _encode_field_name(field_name)
            value_bytes = _encode_field_value(fields[field_name])
            digest.update(
                len(name_bytes).to_bytes(
                    2,
                    byteorder="big",
                ),
            )
            digest.update(name_bytes)
            digest.update(
                len(value_bytes).to_bytes(
                    8,
                    byteorder="big",
                ),
            )
            digest.update(value_bytes)

        return BusinessOperationFingerprint(
            digest=digest.digest(),
            key_version=self._key_version,
        )


def _encode_field_name(field_name: str) -> bytes:
    if _FIELD_NAME_PATTERN.fullmatch(field_name) is None:
        raise ValueError("Business-operation fingerprint field name is invalid")
    encoded = field_name.encode("ascii")
    if len(encoded) > _MAX_FIELD_NAME_BYTES:
        raise ValueError("Business-operation fingerprint field name is invalid")
    return encoded


def _encode_field_value(value: FingerprintFieldValue) -> bytes:
    if isinstance(value, str):
        return value.encode("utf-8")
    if isinstance(value, bytes):
        return value
    raise TypeError("Business-operation fingerprint field value must be str or bytes")
