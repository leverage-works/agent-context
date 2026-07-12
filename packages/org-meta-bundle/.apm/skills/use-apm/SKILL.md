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
in one repository. Local `path:` dependencies MUST live below the repository
root that owns the declaring `apm.yml`; use a repository-relative path such as
`./local-apm-packages/second-brain-workflows`.

Do not use `../` paths, absolute paths, or paths into sibling repositories.
APM may support those forms, but they make a workspace depend on a machine-local
checkout. Put cross-repository workflows in a remote Git or marketplace package
instead.

For example, `second-brain` can keep its context-specific package inside that
repository and declare it as a regular dependency in its root `apm.yml` when
every contributor needs its workflows:

```yaml
dependencies:
  apm:
    - path: ./local-apm-packages/second-brain-workflows
```

Use `devDependencies.apm` only for maintainer-only content, such as test
fixtures, debug agents, and release tooling. APM deploys both dependency groups
on a normal install, but excludes `devDependencies` from `apm pack` output.

Each local package needs its own `apm.yml` and `.apm/` source tree. Install it
from the workspace root after adding or changing a dependency:

```sh
apm install --target codex --dry-run
apm install --target codex
```

A local package is versioned with the repository that owns it and should be
promoted into this organization package repository only when it has a clear
cross-repository use.

## Marketplace Workflow

Validate package versions before building the marketplace artifact:

```sh
apm pack --check-versions --dry-run
apm pack
```

Use local path dependencies while developing packages in the same repository. Install from the published marketplace only after the package release is available.
