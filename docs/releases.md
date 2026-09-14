# Releases

This repository uses the shared Conventional Commit and Semantic Versioning
policy. The bundle, root manifest, and marketplace entry release together as
`vX.Y.Z`. The existing `v0.2.0` tag remains the historical baseline; the next
release is computed from subsequent commits, not manually selected from the
working manifest's development version.

The consumer contract includes package paths and names, skill entry points,
supported script interfaces, required tooling, and the behaviour of installed
instructions. Additive capabilities or guidance use `feat`; corrections use
`fix`; incompatible removals or requirements use a breaking marker and explain
the migration. README-only explanation can use `docs`. A breaking change during
`0.x` advances to `1.0.0`, following the existing CypherDown policy.

## Preview and validation

```sh
make
make release-plan
make release-test
make test
make release-check
```

Planning reads local Git history and tags and writes `build/release/notes.md`.
It does not fetch, commit, tag, or publish. Synchronize tag history before using
its result. `release-check` verifies all three manifest version fields and the
Claude marketplace index. Between releases the index may retain a verified
historical release while development manifests advance; preparation and publication
require it to match the new package exactly. This avoids advertising a nonexistent
tag before the release is prepared. CI also installs the local APM bundle and compiles its
instructions using APM CLI 0.30.0. Both CI and release jobs run the script tests.

## Automatic publication

On a push to `main`, the Release workflow checks out current `main` with full tag
history and queries GitHub for incomplete publication. It then:

1. Resumes a pending metadata commit or an unpublished latest release tag before
   planning newer work; otherwise computes the highest required version bump.
2. Synchronizes root/package/marketplace versions and regenerates the tracked
   marketplace index, then validates tests, metadata, APM installation and compilation.
3. Commits the manifests, marketplace index, and refreshed local-package lockfile
   as `chore(release): vX.Y.Z`, with an explanatory body, and pushes to `main`.
4. Tags that exact commit and creates a draft GitHub release with commit-derived
   notes, including bodies and issue references, before publishing it.

The release is the tagged source tree: consumers install the versioned package
subdirectory directly. GitHub supplies source archives; there are no separately
uploaded binary assets. Marketplace entries point to the immutable version tag;
embedding the release commit's own SHA in that commit would be circular.

Only the workflow performs the release commit and publication. It uses the
repository `GITHUB_TOKEN` with contents-write permission. Repository rules must
allow that bot to push release metadata to `main`; configure that locally rather
than disabling branch protections. A non-fast-forward push fails before creating
a tag. The token's pushes do not recursively trigger ordinary push workflows,
and the metadata commit does not qualify for another version bump in any case.

Workflows serialize release runs. Re-run a failed workflow or manually dispatch
Release on `main` to recover. Matching tags are reused, drafts are resumed, and
published releases are left unchanged. A conflicting tag aborts publication.
If recovery finishes an older release while newer commits are waiting, dispatch
Release again to release those commits. Authentication failures propagate rather
than being interpreted as missing releases. Correct published defects with a new
version; never move a tag.

## Script interface

The CI-only operations are parameterized and therefore have no Make wrappers:

```sh
uv run --script scripts/release/release.py --help
uv run --script scripts/release/release.py prepare --version X.Y.Z
uv run --script scripts/release/release.py publish --version X.Y.Z --commit FULL_SHA --repo OWNER/REPO
```

`prepare` only writes metadata, requires the computed version, and does not
commit. `publish` changes remote tags and GitHub releases, requires the prepared
release commit checked out, and uses `build/release/notes.md`. Normally let the
workflow perform both. `plan --repo OWNER/REPO` adds authenticated, read-only
GitHub checks for publication recovery; the parameterless Make preview stays
local.

## Organization rollout

Start repository dependency onboarding with the shared
[`leverage-works/renovate-config`](https://github.com/leverage-works/renovate-config)
preset. If an organization has published its own preset, projects should extend
that preset, which can extend the shared baseline and add organization policy.
Otherwise, use the baseline directly:

```json
{
  "extends": ["github>leverage-works/renovate-config"]
}
```

Merge this into existing repository configuration, preserving project exceptions.
The public preset supplies shared rules without cross-organization credentials.
Unpinned presets follow their default branch on each run. Pin only to a published
tag when a versioned rollout is needed.

Each organization still owns its runner, credentials, repository selection,
schedules, and merge policy. Adding `extends` does not start Renovate. Onboard the
repo into its organization's runner and validate a real dependency update PR.
Keep these configuration repositories independent of APM and agent-context: they
must not install this bundle or require APM to validate their presets. APM grouping
rules are configuration, not a package dependency.

For APM consumers, use a Renovate version with APM manager support and provide the
APM CLI inside its execution environment so manifest and lockfile updates land
together. Pin consuming repos to a published tag, for example
`leverage-works/agent-context/packages/org-meta-bundle#v0.3.1`; choose the released
version containing the guidance you need. Untagged dependencies are skipped by
Renovate. Local `path:` packages keep their repository lifecycle.

As part of each organization's clone onboarding, integrate advisory `post-merge`
and `post-rewrite` (rebase only) checks without replacing existing hooks. Compare
the trees before and after the operation for changes to `apm.yml` or
`apm.lock.yaml`, including addition or deletion. Rebase handling must retain the
pre-rebase tip and compare it with the completed result, not compare only the
last replayed commit. Implementations should test fast-forward and merge pulls,
rebases, unchanged dependency files, and coexistence with existing hooks.

On a dependency-file change, print:

```text
APM dependencies changed.
Run make apm-install to refresh your skills and instructions.
```

The reminder performs no network lookup, installation, or tracked-file changes,
and must not fail Git. Already-up-to-date pulls stay quiet. No persistent reminder
fingerprint or shell wrapper is needed. After installing, restart the agent
session. Hook implementation and consumer Renovate configuration are separate
organization-owned rollout work, not installed by this package.

References: [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/),
[Semantic Versioning](https://semver.org/),
[Renovate APM manager](https://docs.renovatebot.com/modules/manager/apm/), and
[Git hooks](https://git-scm.com/docs/githooks).
