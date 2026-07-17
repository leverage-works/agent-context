---
name: work-on-gh-issues
description: Use when discovering, selecting, or beginning work on GitHub issues raised against the current repository.
---

# Work on GitHub Issues

Use this skill when picking up work from GitHub issues in the repository that
contains the current checkout. It makes issues raised *against* that repository
discoverable, so each repository can independently pick up its own work.

## List Available Work

From anywhere inside the repository, run:

```sh
uv run .agents/skills/work-on-gh-issues/scripts/list_issues.py
```

The helper resolves the current checkout's `origin` remote, queries its open
GitHub issues, and prints a table with each issue's number, title, author,
opened date, labels, and URL.

To inspect one exact issue, pass its number either positionally or by option:

```sh
uv run .agents/skills/work-on-gh-issues/scripts/list_issues.py 42
uv run .agents/skills/work-on-gh-issues/scripts/list_issues.py --issue 42
```

Use `--state all` to include closed issues, and `--limit 100` when the default
list size is insufficient.

## Pickup Workflow

1. Run the helper before beginning issue-driven work.
2. Select an issue from its table, or use its number directly.
3. Mark the issue as taken immediately by assigning it to the authenticated
   operator:

   ```sh
   gh issue edit <number> --add-assignee @me
   ```

   Do this before implementation. Do not remove or replace another assignee;
   if the issue is already assigned and that indicates active work, stop and
   coordinate instead of taking it over.
4. Read the full issue and its comments with `gh issue view <number>` before
   changing code.
5. Implement and verify the requested work in the current repository.
6. When communicating in another repository, use `collaborate-cross-repos`.
   Keep all GitHub identity conventions from that skill.

## Requirements and Boundaries

- The checkout must have an `origin` remote pointing to GitHub.
- The helper uses the user's existing `gh` authentication; it does not create,
  switch, or expose GitHub credentials.
- It lists issues for the current repository only. Change to the relevant
  checkout before using it to pick up work from another repository.
