.DEFAULT_GOAL := help

.PHONY: help apm-install apm-update test release-test release-plan release-check

help: ## List available repository actions.
	@awk 'BEGIN { FS = ":.*##" } /^[[:alnum:]_.-]+:.*##/ { printf "  %-20s %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

apm-install: ## Install APM dependencies and compile Codex instructions.
	apm install --target codex
	apm compile --target codex

apm-update: ## Update APM dependencies and compile Codex instructions.
	apm install --update --target codex
	apm compile --target codex

release-plan: ## Preview the next version and write release notes under build/.
	uv run --script scripts/release/release.py plan

release-check: ## Validate package and marketplace version alignment.
	uv run --script scripts/release/release.py check

release-test: ## Test version planning and publication recovery.
	uv run --script scripts/release/test_release.py

test: release-test ## Test release tooling and bundled scripts.
	uv run --script scripts/test.py
