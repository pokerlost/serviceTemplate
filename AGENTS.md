# serviceTemplate

Read selected [baseRules](https://raw.githubusercontent.com/serrja/baseRules/bafcb63ed94b9769a0ca098e5db4b33c55dbc1b9/docs/engineering.md),
then [Pokerlost norms](https://raw.githubusercontent.com/pokerlost/projectRules/904c65a3daab88802fb5e414cdaccc7ad2b555a8/docs/project.md),
then the full [local contracts](docs/agent-contracts.md), `TEMPLATE.md`, `copier.yml`
and the SDK compatibility contract before editing. This override covers template
composition, service protocol and SDK-only admission; applications keep their own
contracts/settings/scopes/migrations. Edit the owned overlay, then compose/update.

Pins are reading sources, not automatic loaders or grants. Review the source diff,
change full-SHA links explicitly and run docs checks when refreshing rules.

Daily work uses `dev` and lint only. `main` and `test` stay unchanged until an
explicit promotion. Full acceptance, template render/update checks, builds and
releases are manual; a dev snapshot is not a verified release.
