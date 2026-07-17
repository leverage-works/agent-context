.DEFAULT_GOAL := help

.PHONY: help apm-install apm-update

help: ## List available repository actions.
	@awk 'BEGIN { FS = ":.*##" } /^[[:alnum:]_.-]+:.*##/ { printf "  %-20s %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

apm-install: ## Install APM dependencies and compile Codex instructions.
	apm install --target codex
	apm compile --target codex

apm-update: ## Update APM dependencies and compile Codex instructions.
	apm install --update --target codex
	apm compile --target codex
