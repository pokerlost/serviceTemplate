# Python style

This page summarizes the executable Python quality contract for the generated service.

## Executable source of truth

The project requires Python 3.14 or newer. `pyproject.toml` is authoritative
for the Python requirement, Ruff target, 100-character line length, lint selection, strict mypy
configuration, source roots, and declared development dependencies. `uv.lock` records their
resolved versions.

Ruff owns formatting and linting. Mypy runs in strict mode with Python 3.14 semantics. Pre-commit
invokes those tools through `uv run --locked`, so hook versions come from the project lock instead
of an independent hook environment. Use the commands documented in
`docs/development/commands.md`.

Do not add broad `# noqa` or `# type: ignore` suppressions. A narrow suppression requires a specific, reviewable reason and must not hide an avoidable typing or lint defect.

## Language and dependency conventions

- Use modern Python 3.14 syntax.
- Expose FastAPI dependencies through PEP 695 type aliases backed by private resolver functions.
- Keep public request, response, application, domain, and persistence models in their established layers.
- Preserve explicit imports and focused package facades.
- Keep async boundaries explicit and avoid blocking work in request paths.
- Never log or embed credentials, tokens, private keys, or database URLs.

## Artifact names

Concrete artifact names include their category in both the class suffix and the matching
`snake_case` module suffix. Request, response, persistence model, and projection details remain in
the generated rulebook rather than being repeated here.

The generated `AGENTS.md` is the normative source for the complete naming matrix, layer rules,
allowed base-name exceptions, operation-package naming, and public API conventions. Keep this page
as a tooling summary rather than a duplicate rulebook.
