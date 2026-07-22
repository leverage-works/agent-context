---
description: Require Conventional Commit messages for every Git commit.
applyTo: "**"
---

# Git Commit Messages

Every Git commit created in this repository MUST use the Conventional Commits
format:

```text
<type>(<optional scope>): <description>
```

Examples:

```text
fix: correct test path
chore(renovate): label dependency dashboard
```

Before committing, verify that the commit subject conforms to this format. Do
not create a commit with a plain-English subject that omits the commit type.

After completing a coherent piece of work, suggest a suitable Conventional
Commit message and wait for human review before creating the commit, unless a
human explicitly asks you to commit.
