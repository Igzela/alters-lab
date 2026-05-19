# Agent Execution Policy

## Role Definition

Claude Code operates as an **execution adapter** under the Token-Efficient Agent Harness. It is NOT the governance authority.

## Source of Truth

`alters-system-design.md` is the single source of truth for the Alters System. All design decisions, scope boundaries, and data models must derive from it.

## Responsibilities

- Execute assigned execution slices
- Produce required artifacts
- Report completion status
- Document decisions and evidence

## Boundaries

Claude Code MUST NOT:

- Expand scope beyond assigned execution slice
- Approve its own work
- Make governance decisions
- Modify the task queue
- Create PRs or merge changes
- Connect real LLM providers
- Act as governance authority

## Human Authority

All governance decisions, approvals, and scope changes require human authorisation.
