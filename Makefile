ifneq ($(CONTAINERIZED),1)
QUALITY_IMAGE := servicetemplate:quality
RUNTIME_IMAGE := servicetemplate:candidate
QUALITY_NETWORK := bridge
QUALITY_EXTRA_TARGETS := docs-check format-check chart-check
IMAGE_COMMAND = printf "%s\n" "notApplicable: maintenance source; runtime images belong to rendered applications"
VERIFY_COMMAND = $(MAKE) render RENDER_OUTPUT="$(CURDIR)/.local/verified-render" RENDER_ARGS="-d service_name=verifyService -d withTesting=false -d withCi=false"
BUILD_COMMAND = printf "%s\n" "notApplicable: maintenance source; distributions are verified in disposable renders"
SDK_RENDER ?= $(CURDIR)/.local/verified-render
.PHONY: lock-render
lock-render:
	$(DOCKER) buildx build --file docker/Dockerfile.sdk-lock --secret id=sdk_token,env=SDK_APP_TOKEN --target lock-artifact --output "type=local,dest=$(SDK_RENDER)" $(DOCKER_BUILD_ARGS) "$(SDK_RENDER)"
include docker/quality-python.mk
else
.DEFAULT_GOAL := help

PYTHON ?= $(CURDIR)/.venv/bin/python
UV ?= uv
UVX ?= uvx
PRE_COMMIT_VERSION := 4.6.2
MARKDOWN_DOCUMENTS := $(shell find . -type f \( -name '*.md' -o -name '*.md.jinja' \) \
	-not -path './.git/*' -not -path './.pytest_cache/*' -not -path './.mypy_cache/*' \
	-not -path './.ruff_cache/*' -not -path './.venv/*' \
	-not -path './coverage/*' -not -path './dist/*' \
	-not -path './.agents/*' -not -path './.codex/*' -not -path './backups/*' \
	-not -path './.aws/*' -not -path './.local/*' -not -path './.serena/*' \
	-not -path '*/.github/*' -print)

define require_tool
	@command -v "$(1)" >/dev/null 2>&1 || { echo "Required tool not found: $(1)" >&2; exit 127; }
endef

.PHONY: help install format format-check lint typecheck docs-check pre-commit test compose check check-full

help: ## Show this help message
	$(call require_tool,awk)
	@awk 'BEGIN {FS = ":.*## "} /^[a-zA-Z0-9_-]+:.*## / {printf "  %-18s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install the locked maintenance environment.
	$(UV) sync --locked

format: ## Apply Ruff lint fixes and formatting
	$(call require_tool,$(UV))
	$(UV) run --locked ruff check --fix tools tests
	$(UV) run --locked ruff format tools tests

format-check: ## Check Ruff formatting without changing files
	$(call require_tool,$(UV))
	$(UV) run --locked ruff format --check tools tests

lint: ## Run Ruff lint without changing files
	$(call require_tool,$(UV))
	$(UV) run --locked ruff check tools tests

typecheck: ## Run strict mypy for repository-maintenance scripts
	$(call require_tool,$(UV))
	$(UV) run --locked mypy

pre-commit: ## Run template-maintenance hooks against all files
	$(call require_tool,$(UVX))
	$(UVX) --from 'pre-commit==$(PRE_COMMIT_VERSION)' pre-commit run --all-files --show-diff-on-failure

docs-check: ## Validate Markdown structure, local links and anchors
	$(call require_tool,$(PYTHON))
	$(PYTHON) tools/check_documentation.py --documents $(MARKDOWN_DOCUMENTS)

test: ## Run real Copier updates and maintenance coverage.
	$(UV) run --locked pytest --cov --cov-report=term-missing --cov-report=json --cov-report=xml

compose: ## Verify the inherited source and render a disposable service.
	$(UV) run --locked python tools/compose_template.py --repo . --smoke

check: format-check lint typecheck docs-check test ## Run regular non-mutating maintainer checks
	$(UV) lock --check

check-full: check pre-commit ## Run regular checks and all pre-commit hooks

endif
