---
name: use-apm
description: Use when authoring, installing, validating, or publishing APM packages in a Codex workspace.
---

# Use APM

## Authoring

- Author package content under `.apm/`; do not edit generated deployment output.
- Put each skill in `.apm/skills/<skill-name>/SKILL.md` and keep its supporting scripts, references, and assets beside it.
- Keep package manifests in `apm.yml` with explicit name, version, description, and target selection.

## Codex Workflow

Use a dry run before installing managed package content:

```sh
apm install --target codex --dry-run
apm install --target codex
```

Codex receives skills under `.agents/skills/`. It receives agents under `.codex/agents/` and compiled instructions through `AGENTS.md`; edit package source instead of those generated files.

## Marketplace Workflow

Validate package versions before building the marketplace artifact:

```sh
apm pack --check-versions --dry-run
apm pack
```

Use local path dependencies while developing packages in the same repository. Install from the published marketplace only after the package release is available.
