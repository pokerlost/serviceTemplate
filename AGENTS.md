# serviceTemplate

Read selected [baseRules](https://raw.githubusercontent.com/serrja/baseRules/8434509933feaa71ba312f8d02caad7362766d5a/docs/engineering.md),
then [Pokerlost norms](https://raw.githubusercontent.com/pokerlost/projectRules/c3bfb397c46c2fa1021009e13f9e1090d9078176/docs/project.md),
then the full [local contracts](docs/agent-contracts.md), `TEMPLATE.md`, `copier.yml`
and the SDK compatibility contract before editing. This override covers template
composition, service protocol and SDK-only admission; applications keep their own
contracts/settings/scopes/migrations. Edit the owned overlay, then compose/update.

Pins are reading sources, not automatic loaders or grants. Review the source diff,
change full-SHA links explicitly and run docs checks when refreshing rules.
