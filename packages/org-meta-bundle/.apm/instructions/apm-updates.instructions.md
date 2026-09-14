---
description: Pin released APM dependencies and refresh installations after dependency changes.
applyTo: "**"
---

# APM Dependency Updates

Pin remote APM packages to explicit release versions, for example
`owner/repository/packages/package-name#v1.2.3`. Commit `apm.yml` and
`apm.lock.yaml` together. Repository-local `path:` dependencies remain versioned
with their owning repository.

Each organization owns its Renovate configuration: credentials, schedules,
grouping, review and automerge policy. Shared packages provide guidance, not a
mandatory cross-organization Renovate configuration. Configure Renovate's APM
manager to update version pins and the lockfile together; its runner needs APM
available to regenerate the lockfile. Unversioned dependencies are skipped.

During onboarding, integrate an advisory local check with the repository's
existing Git hooks without replacing them. After a successful merge (including
a fast-forward pull), or a rebase, detect whether `apm.yml` or `apm.lock.yaml`
changed across the operation. For rebase hooks, ignore amend events and compare
the pre-operation and resulting trees rather than only the last replayed commit.
When either file changed, print:

```text
APM dependencies changed.
Run make apm-install to refresh your skills and instructions.
```

The check must not access upstream services, install packages, change tracked
files, or fail the Git operation. Unchanged pulls stay quiet. No persistent
reminder state or shell wrapper is required. Hook installation is local to each
clone and must be included in that organization's onboarding workflow.

`make apm-install` installs the accepted dependency versions and recompiles
instructions. `make apm-update` deliberately resolves newer dependencies and
recompiles; review its lockfile changes. Restart the agent session after refreshing
its skills and instructions.
