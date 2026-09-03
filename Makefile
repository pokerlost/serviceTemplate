.DEFAULT_GOAL := help

PYTHON ?= python3
UVX ?= uvx
RUFF_VERSION := 0.16.4
MYPY_SPEC := mypy>=2.3,<2.4
PRE_COMMIT_VERSION := 4.6.2
MARKDOWN_DOCUMENTS := $(shell find . -type f \( -name '*.md' -o -name '*.md.jinja' \) \
	-not -path './.git/*' -not -path './.pytest_cache/*' -not -path './.mypy_cache/*' \
	-not -path './.ruff_cache/*' -not -path './.venv/*' -print)

define require_tool
	@command -v "$(1)" >/dev/null 2>&1 || { echo "Required tool not found: $(1)" >&2; exit 127; }
endef

.PHONY: help format format-check lint typecheck docs-check pre-commit check check-full

help: ## Show this help message
	$(call require_tool,awk)
	@awk 'BEGIN {FS = ":.*## "} /^[a-zA-Z0-9_-]+:.*## / {printf "  %-18s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

format: ## Apply Ruff lint fixes and formatting
	$(call require_tool,$(UVX))
	$(UVX) --from 'ruff==$(RUFF_VERSION)' ruff check --fix .
	$(UVX) --from 'ruff==$(RUFF_VERSION)' ruff format .

format-check: ## Check Ruff formatting without changing files
	$(call require_tool,$(UVX))
	$(UVX) --from 'ruff==$(RUFF_VERSION)' ruff format --check .

lint: ## Run Ruff lint without changing files
	$(call require_tool,$(UVX))
	$(UVX) --from 'ruff==$(RUFF_VERSION)' ruff check .

typecheck: ## Run strict mypy for repository-maintenance scripts
	$(call require_tool,$(UVX))
	$(UVX) --from '$(MYPY_SPEC)' mypy

pre-commit: ## Run template-maintenance hooks against all files
	$(call require_tool,$(UVX))
	$(UVX) --from 'pre-commit==$(PRE_COMMIT_VERSION)' pre-commit run --all-files --show-diff-on-failure

docs-check: ## Validate Markdown structure and the no-relative-link policy
	$(call require_tool,$(PYTHON))
	$(PYTHON) template/scripts/check_documentation.py --documents $(MARKDOWN_DOCUMENTS)

check: format-check lint typecheck docs-check ## Run regular non-mutating maintainer checks

check-full: check pre-commit ## Run regular checks and all pre-commit hooks
