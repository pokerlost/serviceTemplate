# Changelog

The private SDK gate follows the confirmed canonical `pokerlost/accountsService` identity after its GitHub transfer; the installation remains SDK-only.

All notable template changes are documented here. Releases use PEP 440-compatible Git tags.

## 0.3.0.dev1

Compatible tooling prerelease: inherit source-bound local CI and version/artifact
checks from the Python owner. Derive template stamps from root metadata and render
Copier full-SHA provenance. The application version and answer schema are retained;
no runtime behavior or historical migration changes are introduced.

## Unreleased

- Move access-token authentication from the JSON body to the standard Authorization bearer header.
- Publish exact local scopes through FastAPI's standard OAuth2 client-credentials OpenAPI model.
- Replace `Scope`/`PokerlostScope` with one service-local `Scopes` enum and description catalog.
- Add canonical invalid, expired, missing-authentication, and insufficient-scope failures before
  endpoint execution.
- Pass validated `retry_after` only through the central `PokerlostResponse` error path.
- Document explicit service-owned initial token acquisition, persistent versioned UTC state, and
  one SDK reactive expired-token refresh/replay.
- Use module-level flat routers, Pydantic boundary validation, response-model serialization, and
  service-owned domain enums.
- Allow public-only OpenAPI documents to omit an unused OAuth2 scheme while validating protected
  operation scopes against the explicit SDK catalog.
- Replace task-specific rendered checks with maintained Copier, HTTP, lifecycle, authorization,
  documentation and installed-wheel regression suites.
- Inherit the shared digest-oriented Helm chart, Compose transaction tests and multi-stage
  installed-wheel Docker build from the content-addressed FastAPI parent.
- Keep project tests, settings, scopes, migration history and deployment values during historical
  Copier updates; manage shared technical cases under `tests/foundation/`.
- Require complete statement/branch coverage and report skipped private runtime verification as
  failing. Prepare an environment-approved SDK-only App workflow without configuring credentials
  or publishing images, packages or releases.

No compatibility alias or parallel legacy protocol is retained.
