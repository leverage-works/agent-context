# agent-context

Codex-first APM packages for the personal-leverage organization.

## Onboard a Codex Workspace

Run these commands from the repository where you want Codex to use the
organization workflows.

1. Install APM, then confirm it is on your `PATH`:

   ```sh
   curl -sSL https://aka.ms/apm-unix | sh
   apm --version
   ```

   On macOS or Linux, Homebrew is an alternative:

   ```sh
   brew install microsoft/apm/apm
   ```

2. Bootstrap the workspace manifest. This creates `apm.yml`; choose Codex when
   prompted for a target.

   ```sh
   apm init
   ```

   For a non-interactive setup, use:

   ```sh
   apm init --yes --target codex
   ```

3. Install the organization bundle directly from this repository:

   ```sh
   apm install personal-leverage/agent-context/packages/org-meta-bundle --target codex
   apm compile --target codex
   ```

   This writes skills to `.agents/skills/`, compiles package instructions into
   `AGENTS.md`, and records the dependency in `apm.yml` and `apm.lock.yaml`.
   No marketplace registration or manual manifest editing is required.

4. Reload the Codex agent or start a new Codex session in the workspace. Codex
   reads the installed skills and generated `AGENTS.md` instructions when the
   session starts.

## Makefile Convention

Every repository should use its `Makefile` as the discoverable catalogue of
supported actions. Running `make` must list the available targets and concise
descriptions. Include these standard APM targets:

```make
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
```

To review the planned files before writing them, add `--dry-run` to the install
command.

## Structure

- `packages/` contains independently versioned APM packages.
- `packages/org-meta-bundle/` provides the organization-wide Codex workflows.
- `.agent-cache/` is generated local documentation state.

## Maintain This Repository

This repository installs `org-meta-bundle` from its local package path. Run:

```sh
make
make apm-install
apm run hydrate-cached-docs
```

Use `make apm-update` to refresh APM dependencies before recompiling the
Codex instructions. `make` lists the supported repository actions.

Build the Codex marketplace artifact from the repository root:

```sh
apm pack --check-versions --dry-run
apm pack
```
