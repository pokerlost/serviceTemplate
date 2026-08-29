# Business-operation fingerprinting

This page defines the generated keyed fingerprint primitive for resumable business operations and
the boundary that concrete services must complete.

## Canonical primitive

`application/idempotency/business_operation_fingerprinting.py` provides
`BusinessOperationFingerprinter`, `BusinessOperationFingerprint`, and `FingerprintComparison`.
The fingerprinter computes a deterministic HMAC-SHA-256 digest using a dedicated versioned secret,
a versioned domain separator, sorted field names, and length-prefixed names and values. Field names
use ASCII `snake_case`; values are exact `str` UTF-8 bytes or exact `bytes` values. The component
does not use JSON, `repr()`, Unicode normalization, or ambiguous concatenation.

The immutable fingerprint stores only a 32-byte digest and a positive key version. Its instance
`compare()` method uses `hmac.compare_digest` for digest bytes and requires the same key version.
It returns `MATCH` only when both match; all other candidates return `CONFLICT`. Encoding helpers
are private module functions, and the implementation has no static methods.

## Concrete operation ownership

The pristine service does not instantiate the fingerprinter because it has no idempotent business
operation. A concrete service with such an operation must:

1. require the configured secret during application composition;
2. construct one process-owned `BusinessOperationFingerprinter` from typed settings;
3. inject it into the relevant application handlers;
4. define a small explicit semantic field mapping for each idempotent operation;
5. include an operation discriminator when multiple operation types share one persistence key
   namespace;
6. persist the digest and key version together inside the operation transaction boundary.

Sensitive exact values may be fingerprint inputs when retry equivalence requires them because only
the keyed digest is persisted. Canonical plaintext, fingerprint fields, secrets, and digest bytes
must never be persisted separately, logged, or exposed through an API. A randomized password hash,
model `repr()`, or unframed manual concatenation is not a semantic fingerprint input.

## Key lifecycle

The generated first-version policy does not implement a speculative keyring. Do not rotate the
active fingerprint key until all retained idempotency records produced with the old key have
expired or been deleted. The key version identifies the secret that produced a digest; removing
that secret means old records cannot be recomputed for replay. Without an explicit version-aware
keyring, a candidate produced with another key version is a conflict.

Settings and Kubernetes secret handling are documented in
`docs/getting-started/configuration.md` and
`docs/development/containers-and-kubernetes.md`.
