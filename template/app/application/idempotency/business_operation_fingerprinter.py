"""Keyed deterministic business-operation fingerprinter."""

from __future__ import annotations

import hmac
from collections.abc import Mapping
from hashlib import sha256

from pydantic import SecretStr

from .business_operation_fingerprint import BusinessOperationFingerprint
from .constants import (
    CANONICAL_FORMAT_DOMAIN,
    FIELD_NAME_PATTERN,
    MAX_FIELD_COUNT,
    MAX_FIELD_NAME_BYTES,
)
from .types import FingerprintFieldValue


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
            raise ValueError("Fingerprint secret must contain at least 32 UTF-8 bytes")
        if key_version < 1:
            raise ValueError("Fingerprint key version must be positive")
        self._secret = secret_bytes
        self._key_version = key_version

    def fingerprint(
        self,
        fields: Mapping[str, FingerprintFieldValue],
    ) -> BusinessOperationFingerprint:
        """Hash named exact values in deterministic field-name order."""
        if not fields or len(fields) > MAX_FIELD_COUNT:
            raise ValueError("Fingerprint fields are invalid")

        digest = hmac.new(
            self._secret,
            digestmod=sha256,
        )
        digest.update(CANONICAL_FORMAT_DOMAIN)
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
    if FIELD_NAME_PATTERN.fullmatch(field_name) is None:
        raise ValueError("Fingerprint field name is invalid")
    encoded = field_name.encode("ascii")
    if len(encoded) > MAX_FIELD_NAME_BYTES:
        raise ValueError("Fingerprint field name is invalid")
    return encoded


def _encode_field_value(value: FingerprintFieldValue) -> bytes:
    if isinstance(value, str):
        return value.encode("utf-8")
    if isinstance(value, bytes):
        return value
    raise TypeError("Fingerprint field value must be str or bytes")
