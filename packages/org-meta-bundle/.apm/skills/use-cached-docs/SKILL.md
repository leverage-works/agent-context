---
name: use-cached-docs
description: Use when refreshing cached external documentation, adding cached-docs.yml to an installed skill, or reading locally hydrated tool docs.
---

# Use Cached Docs

## Workflow

1. Search existing cached documentation before using the network.
2. Place a `cached-docs.yml` beside the owning skill's `SKILL.md`.
3. Run the installed hydrator from the workspace root.
4. Keep `.agent-cache/` as generated local state.

## Commands

Preview the releases that would be hydrated:

```sh
uv run .agents/skills/use-cached-docs/scripts/hydrate_cached_docs.py --dry-run
```

Hydrate all manifests discovered beside installed skills:

```sh
uv run .agents/skills/use-cached-docs/scripts/hydrate_cached_docs.py
```

When the consumer defines an APM script, prefer:

```sh
apm run hydrate-cached-docs
```

## Manifest Format

Use stable source IDs across all installed skills. The hydrator resolves `version: latest` to a concrete release tag and writes output under `.agent-cache/tool-docs/<id>/<tag>/`.

```yaml
cached_docs:
  - id: example-tool
    strategy:
      type: github-release-http
      repository: owner/repository
      version: latest
    folders:
      - source: docs
        destination: docs
```

Use one `folders` entry for each release subfolder the skill needs. `source` is relative to the archive root and `destination` is relative to the cache entry.
