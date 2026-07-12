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

## Workspace-Local Packages

Use a local package when its workflows, terminology, or tools only make sense
in one repository. Keep reusable organization-wide workflows in a package from
the organization marketplace instead.

For example, `second-brain` can keep its context-specific package inside that
repository and declare it as a local development dependency in its root
`apm.yml`:

```yaml
devDependencies:
  apm:
    - path: ./local-apm-packages/second-brain-workflows
```

The local package needs its own `apm.yml` and `.apm/` source tree. Install it
from the workspace root after adding or changing the dependency:

```sh
apm install --target codex --dry-run
apm install --target codex
```

Use relative paths so a clone works for every contributor. A local package is
versioned with the repository that owns it and should be promoted into this
organization package repository only when it has a clear cross-repository use.

## Marketplace Workflow

Validate package versions before building the marketplace artifact:

```sh
apm pack --check-versions --dry-run
apm pack
```

Use local path dependencies while developing packages in the same repository. Install from the published marketplace only after the package release is available.
