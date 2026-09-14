---
description: Require Conventional Commit subjects, explanatory bodies, and relevant issue references.
applyTo: "**"
---

# Git Commit Messages

Every Git commit created in this repository MUST use a Conventional Commits
subject:

```text
<type>(<optional scope>)[optional !]: <description>
```

Use `feat` for new functionality, `fix` for corrections, and `perf` for
performance improvements. Mark incompatible changes with `!` before the colon
and explain the migration in a `BREAKING CHANGE:` footer. Follow the shared
release policy when classifying consumer-facing changes.

Every commit message MUST include a body, separated from the subject by a blank
line. Summarise what changed and why, with enough context for someone reading
Git history without the original conversation. Keep detail proportional to the
change; a short paragraph is sufficient for simple changes.

Put relevant GitHub issue references in a footer, separated from the body by a
blank line. Use `Refs #123` for related issues and `Fixes #123` only when the
commit fully resolves the issue. Use `owner/repository#123` for issues in
another repository. Omit references when no relevant issue exists. Put issue
references in the footer rather than the subject.

Examples (issue numbers are illustrative):

```text
fix: correct test path

Resolve fixture paths relative to the test file so the suite can run from
any working directory.

Fixes #123
```

```text
chore(renovate): label dependency dashboard

Apply the dependencies label to the dashboard so maintainers can find it
alongside dependency update requests.

Refs owner/repository#456
```

Before committing, verify that the commit subject conforms to this format. Do
not create a commit with a plain-English subject that omits the commit type.

After completing a coherent piece of work, suggest a suitable Conventional
Commit message and wait for human review before creating the commit, unless a
human explicitly asks you to commit.

When suggesting a commit message for review, show the complete subject, body,
and any issue footer together in one `text` code block.
