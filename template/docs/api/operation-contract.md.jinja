# Operation contract

Pokerlost business APIs use one private JSON operation protocol over HTTPS.

## Operations and paths

Every business operation matches:

```text
operation_id = lowerCamelCase verb name
path         = "/" + operation_id
HTTP method  = POST
```

The exact identifier pattern is `^[a-z][A-Za-z0-9]*$`. Valid examples include `getMe`,
`registerAccount`, and `provisionHuman`. Dots, underscores, hyphens, and uppercase initials are
invalid. The generator validates all source documents together and rejects global operation or
schema collisions before writing.

`GET /`, `GET /getOpenApi`, and existing health probes are public bodyless infrastructure
exceptions. Business GET bodies and other business HTTP methods are unsupported.

Each router is one flat module with a factory and decorator. Do not use nested router directories,
imperative registration, route constants, or post-hoc mutation.

## Requests

A public operation accepts `PokerlostRequest[Payload]`:

```json
{
  "payload": {
    "username": "alice"
  }
}
```

A protected operation accepts `PokerlostAuthorizedRequest[Payload]`:

```json
{
  "authorization": {
    "access_token": "secret-value"
  },
  "payload": {}
}
```

Payload types are named closed Pydantic models with snake_case wire fields. Requests do not use
business path/query parameters, cookies, form data, caller-supplied transport metadata, embedded
anonymous bodies, or manual content negotiation.

## Responses

Every success and handled failure uses `PokerlostResponse`. Routes publish the typed success model
and `PokerlostResponse[None]` for expected failures. The five-field invariant is documented in
`docs/api/pokerlost-response.md`.

## Scopes

Scope IDs are separate from operation IDs. Protected routes declare exact values through FastAPI
`Security`, while the matching SDK method declares the same `required_scopes` tuple. See
`docs/api/body-authorization.md`.
