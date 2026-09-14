---
description: Onboard dependency updates with shared Renovate presets and keep versioned APM installations current.
applyTo: "**"
---

# Dependency Management and APM Updates

## Repository onboarding

When onboarding dependency management, inspect the repository's existing Renovate
configuration and runner before adding anything. Reuse the organization's preset
when one is published. The shared baseline is
`github>leverage-works/renovate-config`; organizations can extend it with their own
policies, and projects should extend their organization preset. If no organization
preset exists, extend the shared baseline directly in `renovate.json`:

```json
{
  "extends": ["github>leverage-works/renovate-config"]
}
```

Keep project exceptions local rather than copying the shared rules. Unpinned
presets follow their default branch on each Renovate run; use an existing release
tag when a controlled, versioned rollout is required. Do not assume an example
organization preset or tag has been published.

A preset supplies policy, not a running bot. Each organization owns runner
onboarding, credentials, repository access, schedules, and merge policy. Validate
the configuration and verify an actual update PR before treating onboarding as
complete. Private target repositories still require organization-scoped access,
even when the shared preset and APM packages are public.

Keep Renovate configuration repositories independent of APM: no APM manifests,
lockfiles, installed skills, or APM bootstrap steps. A preset may describe APM
update rules without depending on APM. Tooling needed to refresh consumer
lockfiles belongs in the consumer update runner.

## APM dependencies

Pin remote APM packages to explicit release versions, for example
`owner/repository/packages/package-name#v1.2.3`. Commit `apm.yml` and
`apm.lock.yaml` together. Repository-local `path:` dependencies remain versioned
with their owning repository.

Use a Renovate version with APM manager support to update version pins and the
lockfile together. Its execution environment needs the APM CLI available to
regenerate the lockfile. Unversioned dependencies are skipped. This package
provides adoption guidance; it does not install Renovate configuration or hooks.

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
