---
description: Expose standard project actions through Make and parameterised operations through scripts.
applyTo: "**"
---

# Repository Actions

Use the repository `Makefile` as the discoverable catalogue of standard project
actions that work without caller-supplied parameters.

- Run `make` first to discover available actions.
- Prefer an existing `make <target>` when it matches the intended action.
- When adding or changing a standard project action, add or update its
  documented Make target.
- The default `make` target MUST list the available targets and their concise
  descriptions.
- Use descriptive action names, declare action targets `.PHONY`, and keep
  recipes short. Delegate substantial logic to scripts.
- A target may call a script with fixed arguments that define a useful project
  action, such as checking the project's documentation directory.
- For operations requiring caller-supplied inputs or options, document the
  script invocation and provide useful `--help`. Avoid Make wrappers that
  mainly forward variables such as `INPUT`, `VERSION`, or `ARGS`.

Do not assume a target exists: inspect the Makefile or run `make` before using
one. Use the documented script interface when the operation needs parameters.
