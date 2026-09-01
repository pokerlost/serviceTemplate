# Changelog

All notable template changes are documented here. Releases use PEP 440-compatible Git tags.

## Unreleased

- Replace the previous transport contract with the private Pokerlost body-only JSON protocol over
  HTTPS.
- Use single lowerCamelCase operation IDs, POST business calls, and flat router modules.
- Adopt `PokerlostRequest`, `PokerlostAuthorizedRequest`, and the five-field
  `PokerlostResponse` envelope from the flat SDK facade.
- Add an empty exact-scope catalog, a transport-independent `PokerlostTokenVerifier` port, and a
  fail-closed FastAPI body-authorization dependency without a production verifier.
- Publish unmodified FastAPI OpenAPI without service identity or custom extensions; represent
  protected calls through their body schema.
- Replace caller-controlled request correlation with a server-generated internal request ID.
- Document authorization/retry middleware ordering, body token acquisition and refresh, exact
  scope verification, body `retry_after`, and the no-replay authentication rule.
- Remove the obsolete generic business replay helper and its settings, documentation, and
  deployment configuration.
- Remove unused ORM/request schema facades, the unused projection/result-reader framework, and the
  unconsumed entity-repository convenience base.
- Keep the private SDK source pinned to an immutable pushed revision and update the Copier render
  regression for the new contract.

No compatibility alias or parallel legacy protocol is retained.
