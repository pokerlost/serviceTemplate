# Business-operation fingerprinting

This page defines the generated keyed fingerprint primitive for resumable business operations and
the boundary that concrete services complete.

## Focused package

The canonical implementation lives under `application/idempotency`:

```text
application/idempotency/
├── __init__.py
├── constants.py
├── enums.py
├── types.py
├── business_operation_fingerprint.py
└── business_operation_fingerprinter.py
```

`constants.py` owns the protocol domain, field grammar, and framing limits. `enums.py` owns
`FingerprintComparison`; `types.py` owns `FingerprintFieldValue`; the immutable fingerprint value
owns comparison; and the process-owned fingerprinter owns HMAC construction and private encoding
helpers.

## Canonical v2 format

The exact domain separator is:

```python
b"pokerlost.businessOperationFingerprint.v2\x00"
```

Semantic field names match ASCII lowerCamelCase:

```text
^[a-z][A-Za-z0-9]*$
```

Examples include `operationName`, `businessOperationId`, `accountId`, `principalId`,
`oauthClientId`, and `requestedScopes`. Underscores, hyphens, dots, uppercase initials, non-ASCII
characters, and empty names are invalid.

The fingerprinter preserves these cryptographic and framing rules:

- HMAC-SHA-256 with a dedicated secret of at least 32 UTF-8 bytes;
- deterministic lexicographically sorted field-name order;
- an unsigned 2-byte field count;
- unsigned 2-byte name lengths and unsigned 8-byte value lengths;
- exact UTF-8 bytes for `str` values and exact bytes for `bytes` values;
- no JSON, `repr()`, Unicode normalization, plaintext persistence, or unframed concatenation;
- a 32-byte digest and positive secret `key_version`.

`key_version` identifies the configured secret. The v2 suffix in the domain identifies the
serialization format; these are separate version dimensions.

## Concrete operation ownership

The pristine service does not instantiate the fingerprinter because it has no idempotent business
operation. A concrete service with such an operation must:

1. require the configured secret during application composition;
2. construct one process-owned `BusinessOperationFingerprinter`;
3. inject it into the relevant application handlers;
4. define a small explicit lowerCamelCase semantic field mapping;
5. include an operation discriminator when operation types share one persistence-key namespace;
6. persist the digest and key version together inside the operation transaction boundary.

For example:

```python
fingerprint = fingerprinter.fingerprint(
    {
        "operationName": "accounts.register",
        "businessOperationId": str(command.business_operation_id),
        "username": command.username,
        "nickname": command.nickname,
        "password": command.password.get_secret_value(),
    },
)
```

Sensitive exact values may be inputs when retry equivalence requires them because only the keyed
digest is persisted. Never persist or log the canonical plaintext, mapping fields, secret, or
digest and never expose them through an API.

## Comparison and key lifecycle

`BusinessOperationFingerprint.compare()` uses `hmac.compare_digest` for digest bytes. Equal digest
and equal key version returns `MATCH`; every other candidate returns `CONFLICT`. Comparison is an
instance method, and encoding helpers are private module functions.

Do not rotate the active key until all retained records produced with the old key have expired or
been deleted. A candidate produced by another key version is a conflict.

The camelCase v2 format is a coordinated pre-production break. Clear disposable records produced
by the former format before enabling v2. Do not add dual-format runtime comparison and do not claim
that prior replays remain comparable.

Settings and Kubernetes secret handling are documented in
`docs/getting-started/configuration.md` and
`docs/development/containers-and-kubernetes.md`.
