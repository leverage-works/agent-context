---
description: Use the repository Makefile as the discoverable catalogue of supported actions.
---

# Repository Actions

Treat the repository `Makefile` as the authoritative catalogue of supported
development actions.

- Run `make` first to discover available actions.
- Prefer `make <target>` over running an equivalent underlying command
  directly.
- When adding or changing a supported workflow, add or update a documented
  Make target for it.
- The default `make` target MUST list the available targets and their concise
  descriptions.

Do not assume a target exists: inspect the Makefile or run `make` before using
one.
