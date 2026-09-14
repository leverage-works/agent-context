---
description: Use Bash for simple scripts and Python with uv, inline dependencies, and behavioral tests for substantial automation.
applyTo: "**"
---

# Repository Scripting

Choose the scripting language by complexity and purpose, rather than a line
count.

- Bash is suitable for straightforward command sequences, simple checks,
  redirects, and pipelines.
- Use Python for substantial branching, structured-data processing, retries,
  cleanup handling, or orchestration that benefits from functions and tests.
- Run standalone Python entry points with `uv run --script`. Declare
  `requires-python` and `dependencies` in PEP 723 inline metadata, including
  `dependencies = []` for scripts that only use the standard library.
- Include the third-party dependencies needed by imported local helpers in
  the entry point's metadata. Imported helper modules do not need their own
  metadata blocks.
- Keep shell integration and bootstrap code in the appropriate shell. For
  Python tooling that depends on an established project environment, use that
  environment's dependency and execution conventions.
- Keep substantial logic in importable functions and the CLI entry point
  small. Document parameterised script invocations and provide useful `--help`.

## Testing Scripts

Scripts with substantial logic or consequential side effects should have
automated tests. Scale tests to the behavior and consequences of failure.

- Prefer the standard-library `unittest` framework unless the repository has
  an established alternative. Follow its existing test layout; otherwise,
  keep tests beside a cohesive script group or in a `tests/` directory.
- Test observable behavior, relevant failure cases, and repeat execution
  where idempotency or recovery matters. Avoid tests that merely mirror the
  implementation or wrap trivial commands.
- Use temporary files and databases for fixtures, and fake or mock external
  commands and services. Add integration tests when real process or service
  interaction matters, using disposable resources and documented prerequisites.
- Expose focused suites through documented Make actions and include them in
  the appropriate aggregate suite. Keep live integration checks separately
  selectable and respect repository-specific test isolation requirements.
- Declare the runtime and dependencies needed by the test environment.
  Standalone test entry points also use uv and PEP 723; project-managed suites
  use their existing environment. Do not rely on ambient packages or skip
  intended tests because required dependencies are missing. Importing a script
  does not provision the dependencies in its inline metadata.
