---
name: collaborate-cross-repos
description: Use when creating GitHub issues or replying to GitHub issue or pull-request comments on behalf of one repository in another repository.
---

# Collaborate Across Repositories

Use this skill for every GitHub issue, issue comment, or pull-request comment
sent from one repository to another. The GitHub account is the user's account,
not an agent identity. Make the represented repository clear in the message
itself.

## Represented Repository

Before writing, identify the repository on whose behalf you are communicating:

1. Prefer the current checkout's `origin` repository and use its repository
   name (for example, `payments` from `leverage-works/payments`).
2. If the checkout has no unambiguous origin, use the repository name
   explicitly named by the task.
3. If neither establishes a repository, stop and ask the user; do not guess or
   use the GitHub account name as a substitute.

The represented repository is normally the repository containing the work,
dependency, or maintainer concern that prompted the message. It is not the
repository receiving the issue unless they are the same repository.

## Required Message Opening

Every new cross-repository issue and every reply to a GitHub comment MUST start
with this exact first sentence, replacing the placeholder with the represented
repository name:

```text
As <repo-name> maintainer, ...
```

For example:

```text
As payments maintainer, could you clarify whether v2.4 is compatible with Node 22?
```

Place this sentence before headings, greetings, quoted text, checklists,
context, or links. Do not use a different identity line, signature, agent
name, personal name, bot name, or GitHub handle. The user's authenticated
GitHub identity is sufficient for attribution; the text supplies the
repository-level identity.

## Workflow

1. Confirm the destination repository, issue or pull-request number when
   applicable, and the represented repository.
2. Draft the message beginning with the required sentence. Keep the remaining
   text factual, specific, and actionable.
3. Review the final body immediately before posting: its first characters must
   be `As ` and its first sentence must match `As <repo-name> maintainer,`.
4. Post using `gh` under the user's existing authenticated identity. Do not
   change accounts, configure a separate agent account, impersonate a person,
   or add an automated signature.

## Examples

New issue body:

```markdown
As web-app maintainer, upgrading your SDK to v3 breaks our production build because the `WidgetOptions` export was removed.

Could you document the supported replacement or restore a compatible export?
```

Reply to an issue or pull-request comment:

```markdown
As web-app maintainer, we confirmed that the failure remains on v3.1.2 with a clean lockfile. The minimal reproduction is linked above.
```

## Do Not Use This For

Do not add the prefix to internal repository discussion unless the task is
actually communicating across repositories. Do not omit the prefix merely
because a prior message in the thread already used it: every comment must
identify the represented repository again.
