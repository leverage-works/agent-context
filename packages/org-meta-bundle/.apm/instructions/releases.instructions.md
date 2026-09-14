---
description: Use Conventional Commits, Semantic Versioning, and immutable automated releases.
applyTo: "**"
---

# Versions and Releases

Use Conventional Commits across repositories and Semantic Versioning for released
packages, applications, and other consumer-facing artifacts. Document each
artifact's compatibility contract and whether related packages release together
or independently.

Determine the next version from commits since the latest reachable release tag.
Use the highest applicable bump: `feat` advances minor, `fix` or `perf` advances
patch, and `!` or a `BREAKING CHANGE:` footer advances major. This organization
policy also applies during `0.x`; a breaking change advances to `1.0.0`. Other
commit types do not independently trigger a release unless marked breaking.

Classify changes by consumer impact, not file extension. Skills and instructions
are shipped functionality in an agent package: new capabilities or guidance can
be `feat`, and corrections can be `fix`. Use `docs` for explanatory documentation
that does not change the shipped behaviour. Describe breaking changes and the
required migration explicitly.

Release eligible changes automatically after they reach `main` and required
checks pass. Provide a local, non-publishing release preview. Derive release notes
from commits, retaining useful body and breaking-change details. Keep package
versions, marketplace metadata, and the release tag consistent at the tagged
commit. Metadata-only release commits must not trigger another version bump.

Use immutable `vX.Y.Z` tags for a single release stream; document package-specific
tag schemes for independent streams. Never move published tags or replace
published artifacts. Make retries reuse matching tags and resume drafts; fail
when an existing tag points to a different commit. Publish a corrective version
for defects in a completed release. Test version planning and consequential
publication behaviour, including partial failure and repeat execution.

Keep release tooling consistent with the scripting and Makefile conventions.
Expose parameterless planning and testing actions through Make, and document
parameterized operations through their scripts and `--help`.
