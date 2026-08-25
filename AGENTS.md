# serviceTemplate

This repository is the shared Copier template for PokerLost backend services.

Before changing the template:

1. Read `TEMPLATE.md`.
2. Read `copier.yml`.
3. Inspect the current template structure.
4. Keep the generated service free of business/domain implementation.
5. Keep PostgreSQL as an unconditional part of the base stack.
6. Do not add Copier questions unless generation genuinely depends on the answer.
7. Keep `service_name` as the only user-supplied service identity input unless explicitly changed by the user.
8. Verify both a fresh `copier copy` and, when template-managed files change, `copier update`.

The generated service has its own `AGENTS.md` and `SERVICE.md`.
Do not put service-specific rules in this repository's `AGENTS.md`.
