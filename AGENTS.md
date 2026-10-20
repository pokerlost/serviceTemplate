# serviceTemplate

Read selected [baseRules](https://raw.githubusercontent.com/serrja/baseRules/730418d3cc480b4f05b88b4c8275296c4845a75a/docs/engineering.md),
then [Pokerlost norms](https://raw.githubusercontent.com/pokerlost/projectRules/4785546cffa58f7ae1c22b6d6b8846a0141793eb/docs/project.md),
then the full [local contracts](docs/agent-contracts.md), `TEMPLATE.md`, `copier.yml`
and the SDK compatibility contract before editing. This override covers template
composition, service protocol and SDK-only admission; applications keep their own
contracts/settings/scopes/migrations. Edit the owned overlay, then compose/update.

Pins are reading sources, not automatic loaders or grants. Review the source diff,
change full-SHA links explicitly and run docs checks when refreshing rules.
