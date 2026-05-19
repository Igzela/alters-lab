# Decision Record

## Template

### Decision [ID]

**Date**: YYYY-MM-DD
**Status**: proposed | accepted | rejected | superseded
**Context**: What situation necessitated this decision?
**Decision**: What was decided?
**Consequences**: What are the trade-offs?
**Alternatives**: What other options were considered?

## Decisions

### Decision ALT-002-01: Phase 0 intake remains file-based

**Date**: 2026-05-19
**Status**: accepted
**Context**: ALT-002 implements the snapshot intake workflow. The question was whether to introduce any application code for intake or keep it file-based.
**Decision**: Phase 0 intake remains entirely file-based. No backend, frontend, database, or LLM provider code. The intake workflow is a manual process documented in intake-workflow.md, with snapshot.yaml as the sole output artifact.
**Consequences**: Intake is slower and requires manual effort, but keeps Phase 0 scope minimal and avoids premature complexity. The workflow can be automated in later phases once the file-based process is validated.
**Alternatives**: Build a CLI intake tool (deferred to later phases). Build a web intake form (deferred to later phases).
