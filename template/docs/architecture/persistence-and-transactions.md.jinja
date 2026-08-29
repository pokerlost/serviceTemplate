# Persistence and transactions

This page is the canonical ownership contract for PostgreSQL, SQLAlchemy sessions, repositories,
and Alembic in the generated service.

## PostgreSQL ownership

PostgreSQL is the unconditional source of truth for persisted service state. The process owns one
async engine and session factory in application lifespan. A database-consuming request owns one
`AsyncSession`; sessions are not shared between requests.

The database dependency uses SQLAlchemy's transaction context directly:

```python
async with resources.session_factory.begin() as session:
    yield session
```

Normal context exit commits, exceptional exit rolls back, and context completion closes the
session. Routes, application handlers, repositories, and query adapters do not call `begin()`,
`commit()`, or `rollback()`.

## Persistence adapters

Repositories and query adapters receive the request session and execute explicit SQLAlchemy 2
statements. They do not create engines or sessions and do not complete the transaction. ORM
entities, persistence projections, and public API response models remain separate artifacts.

The pristine template supplies metadata, repository, result-reader, and projection foundations but
no concrete table or business repository. Concrete adapters are added only for responsibilities
defined in `SERVICE.md`.

## Remote calls

Do not hold a PostgreSQL transaction open across a remote `pypokerlost` SDK call. A remote method
call and a local database transaction cannot form one atomic transaction. Structure the application
workflow so remote I/O and a short local persistence phase have explicit ordering and failure
semantics, without treating either side as a distributed commit participant.

## Failure mapping

The engine boundary narrowly converts an exact driver `ConnectionRefusedError` into SQLAlchemy's
`OperationalError`. The centralized API handler maps that availability category to a safe `503`
response. Other `SQLAlchemyError` instances become sanitized `500` responses. The request
dependency does not catch or translate these exceptions.

The exact public forms live in `docs/api/errors.md`. The root probe does not open a session or
establish database readiness; see `docs/api/public-surface.md`.

## Alembic metadata

Alembic owns schema migrations against the shared `Base.metadata`. Every concrete ORM model must be
imported through `persistence.database.models` so migration autogeneration can see it. Do not add a
fake baseline model or migration to an otherwise pristine service. The command workflow and review
discipline are documented in `docs/development/database-migrations.md`.
