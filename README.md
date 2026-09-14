# agent-context

Codex-first APM packages for the leverage-works organization.

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
   apm install leverage-works/agent-context/packages/org-meta-bundle --target codex
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
standard project actions that work without caller-supplied parameters, such as
`make test`, `make build`, or `make docs-check`. Running `make` must list the
available targets and concise descriptions. Declare action targets `.PHONY`
and keep recipes short, delegating substantial logic to scripts.

For operations requiring inputs or options, document the script directly and
provide useful `--help`. Avoid Make targets that mainly forward `INPUT=...`,
`VERSION=...`, or `ARGS=...`. A target may supply fixed arguments that define a
standard project action.

For example, a repository with a documentation checker could expose its usual
check through Make and document custom inputs through the script:

```make
.PHONY: docs-check
docs-check: ## Check the project's documentation.
	uv run --script scripts/check_docs.py --root docs
```

```sh
uv run --script scripts/check_docs.py --help
uv run --script scripts/check_docs.py --root other-docs
```

Prefer an existing Make target when it matches the intended action; otherwise,
use the documented script interface. Include these standard APM targets:

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

## Scripting Convention

Use Bash for straightforward command sequences, simple checks, redirects, and
pipelines. Use Python when a script grows substantial branching, structured-data
processing, retries, cleanup handling, or orchestration. Complexity and purpose
determine the choice, rather than a line limit. Shell integration and bootstrap
code can stay in the appropriate shell.

Run standalone Python scripts with `uv run --script` and declare their runtime
and dependencies using PEP 723. For example, a standard-library-only entry point
can start with:

```python
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
```

Choose the Python requirement for the script; this example does not prescribe
an organization-wide version. Declare third-party dependencies in the same
block, including those used by imported local helpers. Helper modules do not
need their own metadata. Tooling that depends on an established Python project
environment should use that environment's conventions.

Keep substantial logic importable and the CLI entry point small. Scripts with
substantial logic or consequential side effects should have behavioral tests,
covering relevant failures and repeat execution where appropriate. Prefer
`unittest`, temporary fixtures, and fake external interactions, following the
repository's existing test layout and isolation rules. Add integration tests
where real process or service interaction matters.

Expose focused test suites through documented Make actions and include them in
the appropriate aggregate suite. Keep live integration checks separately
selectable. Standalone test entry points also use uv and PEP 723; importing the
script under test does not install its inline dependencies. Declare the test
environment's dependencies so intended tests run without ambient packages or
missing-dependency skips. Existing project-managed suites retain their own
environment conventions.

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
