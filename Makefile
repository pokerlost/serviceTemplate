.DEFAULT_GOAL := help

PYTHON ?= python3
UVX ?= uvx
RUFF_VERSION := 0.16.4
MYPY_SPEC := mypy>=2.3,<2.4
PRE_COMMIT_VERSION := 4.6.2
COPIER_VERSION := 9.17.2
TEMPLATE_SERVICE_NAME := exampleService
MARKDOWN_DOCUMENTS := $(shell find . -type f \( -name '*.md' -o -name '*.md.jinja' \) -not -path './.git/*' -print)

define require_tool
	@command -v "$(1)" >/dev/null 2>&1 || { echo "Required tool not found: $(1)" >&2; exit 127; }
endef

.PHONY: help format format-check lint typecheck docs-check pre-commit template-copy template-check check check-full

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

define run_template_workflow
	$(call require_tool,$(UVX))
	$(call require_tool,$(PYTHON))
	@set -eu; \
	destination="$$(mktemp -d /tmp/pokerlost-service-template.XXXXXX)"; \
	case "$$destination" in /tmp/pokerlost-service-template.*) ;; *) exit 2 ;; esac; \
	trap 'rm -rf -- "$$destination"' EXIT; \
	$(UVX) --from 'copier==$(COPIER_VERSION)' copier copy --defaults \
		--data service_name='$(TEMPLATE_SERVICE_NAME)' . "$$destination"; \
	$(PYTHON) scripts/check_rendered_template.py $(1) "$$destination"
endef

template-copy: ## Render and inspect one disposable fresh service
	$(call run_template_workflow,copy)

template-check: ## Render and statically verify one disposable fresh service
	$(call run_template_workflow,check)

check: format-check lint typecheck docs-check template-check ## Run regular non-mutating maintainer checks

check-full: check pre-commit ## Run regular checks and all pre-commit hooks
