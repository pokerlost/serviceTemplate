# Developing serviceTemplate

The native source workflow is `make install`, `make ci-local`. Its ordered targets
run quality/source tests once, report coverage, build a deterministic source bundle,
verify its bytes and validate release metadata. `coverage/ci-local.json` records
source commit, dirty/content identity, commands, tools and artifact checksums.
Coverage below 100% warns; failed, missing or stale checks never count as PASS.

`OFFLINE=1` requires the exact prepared quality image and all test inputs. The
[canonical tooling guide](https://github.com/serrja/pythonTemplate/blob/main/docs/engineering.md)
owns the Make/receipt implementation. See [versions](versioning.md) and the
[shared development policy](https://github.com/serrja/baseRules/blob/main/docs/development.md).

For a generated service, use the existing SDK-only secret or a verified private bare
SDK cache through the documented `DOCKER_BUILD_ARGS` in [TEMPLATE.md](../TEMPLATE.md#local-source-only-sdk-build).
Neither mode changes the SDK pin or grants access. Persistence checks use unique
Compose projects with synthetic PostgreSQL data and remove only their own resources.

Generated offline CI reuses source-bound wheel/sdist and installed SDK images from
a successful online run. It reruns acceptance without SDK fetches or image builds;
persistence also requires its pinned local Compose images. Missing or changed
inputs are blocked by the inherited Python/FastAPI preflight.
