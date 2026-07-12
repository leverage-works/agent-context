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

3. Register this repository as an APM marketplace, then install the
   organization bundle:

   ```sh
   apm marketplace add personal-leverage/agent-context
   apm install org-meta-bundle@agent-context --target codex
   ```

   This writes the bundle to `.agents/skills/` in the workspace and records it
   in `apm.yml` and `apm.lock.yaml`.

4. Reload the Codex agent or start a new Codex session in the workspace. Codex
   reads the installed skills and generated instructions when the session starts.

To review the planned files before writing them, add `--dry-run` to the install
command.

## Structure

- `packages/` contains independently versioned APM packages.
- `packages/org-meta-bundle/` provides the organization-wide Codex workflows.
- `.agent-cache/` is generated local documentation state.

## Maintain This Repository

This repository installs `org-meta-bundle` from its local package path. Run:

```sh
apm install --dev ./packages/org-meta-bundle --target codex --dry-run
apm install --dev ./packages/org-meta-bundle --target codex
apm run hydrate-cached-docs
```

Build the Codex marketplace artifact from the repository root:

```sh
apm pack --check-versions --dry-run
apm pack
```
