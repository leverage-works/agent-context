# agent-context

Codex-first APM packages for the personal-leverage organization.

## Structure

- `packages/` contains independently versioned APM packages.
- `packages/org-meta-bundle/` provides the organization-wide Codex workflows.
- `.agent-cache/` is generated local documentation state.

## Local Development

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
