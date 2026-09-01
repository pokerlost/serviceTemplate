"""Canonical business-operation fingerprint format constants."""

from __future__ import annotations

import re
from typing import Final

CANONICAL_FORMAT_DOMAIN: Final[bytes] = b"pokerlost.businessOperationFingerprint.v2\x00"
FIELD_NAME_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"[a-z][A-Za-z0-9]*",
    flags=re.ASCII,
)
MAX_FIELD_COUNT: Final[int] = 65_535
MAX_FIELD_NAME_BYTES: Final[int] = 65_535
