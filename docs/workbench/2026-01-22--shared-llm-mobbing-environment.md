# Shared LLM Mobbing Environment

## Goal

Create a shared environment where an LLM works against a repository while
multiple team members can prompt it, observe what it is doing and steer the
same session. The intended interaction is mob programming with an LLM, rather
than several people using isolated assistants.

The agent may need to edit files, run commands and tests, and return changes to
the repository through a controlled branch or pull request.

## Required capabilities

- A shared transcript containing prompts, tool calls, command output, patches
  and test results.
- A shared execution environment tied to a specific repository revision.
- Multi-user steering and approval controls.
- Session history that can be reviewed or replayed.
- Controlled repository write-back.
- Isolated credentials and explicit approval gates for consequential actions.

## Proposed architecture

A minimal custom implementation would contain:

- a web interface for sessions, prompts, live events and approvals;
- an agent orchestrator running the model and tool loop;
- an isolated container, VM or worktree for each session;
- GitHub App integration for repository access and pull requests; and
- an append-only event store as the authoritative session history.

## Pilot questions

- How often must the agent execute code rather than answer questions?
- Is simultaneous control necessary, or are shared transcripts and pull
  requests sufficient?
- How much human review is required for a successful task?
- What are the model, compute and operational costs?

## Status

No product or architecture was selected and no pilot was reported. Vendor
products mentioned in the conversation were transient possibilities, not
decisions. Their capabilities would need to be verified before evaluation.
