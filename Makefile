.DEFAULT_GOAL := help

PYTHON ?= python3
UVX ?= uvx
PRE_COMMIT_VERSION := 4.6.2

define require_tool
	@command -v "$(1)" >/dev/null 2>&1 || { echo "Required tool not found: $(1)" >&2; exit 127; }
endef

.PHONY: help pre-commit docs-check template-copy template-check check check-full

help: ## Show this help message
	$(call require_tool,awk)
	@awk 'BEGIN {FS = ":.*## "} /^[a-zA-Z0-9_-]+:.*## / {printf "  %-18s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

pre-commit: ## Run template-maintenance hooks against all files
	$(call require_tool,$(UVX))
	$(UVX) --from 'pre-commit==$(PRE_COMMIT_VERSION)' pre-commit run --all-files --show-diff-on-failure

docs-check: ## Validate root documentation links and structure
	$(call require_tool,$(PYTHON))
	$(PYTHON) template/scripts/check_documentation.py --documents README.md TEMPLATE.md CREATE_SERVICE.md SDK_COMPATIBILITY.md CHANGELOG.md AGENTS.md

template-copy: ## Render and inspect a disposable fresh Copier service
	$(call require_tool,$(PYTHON))
	$(PYTHON) scripts/verify_template.py --copy-only

template-check: ## Render and run generated-service checks in a disposable directory
	$(call require_tool,$(PYTHON))
	$(PYTHON) scripts/verify_template.py

check: docs-check pre-commit ## Run focused template-maintainer checks

check-full: check template-check ## Run maintainer checks and disposable generated-service verification
