# Changelog

All notable template changes are documented here. Releases use PEP 440-compatible Git tags.

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
- Remove the task-specific rendered-template checker and do not replace it with permanent tests.

No compatibility alias or parallel legacy protocol is retained.
