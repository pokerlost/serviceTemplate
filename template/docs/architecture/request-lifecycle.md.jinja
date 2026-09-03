# Request lifecycle

This page traces composition, server-owned request context, authorization, application execution,
and response handling.

## Composition

`create_app()` resolves settings, configures observability, constructs FastAPI, and registers
request middleware, exception handlers, flat routers, and instrumentation. Lifespan creates the
database engine/session factory and stores them with the optional `PokerlostTokenVerifier` in
`ApplicationResources`.

The pristine service supplies no verifier. A concrete service passes a real local verifier only
when it implements a protected route. Missing protected composition fails closed.

## Inbound flow

```text
FastAPI
→ server-generated request ID
→ dependencies
→ flat route
→ application handler
→ persistence adapter
→ plain success mapping
→ FastAPI response_model
```

The request ID is generated server-side and exists only in request state and telemetry. No caller
correlation value is accepted or returned as a transport contract.

Every business route receives the pure JSON `PokerlostRequest[Payload]`. A protected route also
declares a non-empty exact scope set through `Security`. The standard OAuth2 dependency parses the
bearer header, invokes the local verifier for the exact service audience, and checks every scope
before the route executes.

Routes translate Pydantic-validated payloads into application commands/queries and translate
application results into plain response mappings. FastAPI validates and serializes normal
successes through `response_model`. Central handlers alone build failure envelopes while
normalizing validation, application, database, authentication, authorization, and unexpected
failures without exposing submitted input.

An expired token is rejected before entering the endpoint handler or beginning business effects.
That ordering is the safety invariant for the SDK's one permitted reactive refresh and replay.

## Transactions and outbound calls

A route that declares `DatabaseSession` owns one async transaction. It must end before token
acquisition, outbound SDK calls, retry sleep, or subsequent attempts. Outbound clients use retry
then authorization middleware as documented in `docs/architecture/inter-service-clients.md`.

The root and OpenAPI routes stop at the route layer and open no database transaction.
