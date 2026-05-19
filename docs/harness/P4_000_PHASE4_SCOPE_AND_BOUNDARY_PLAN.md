# P4-000: Phase 4 Scope and Boundary Plan

## Phase 4 Identity

**Name**: Dialogue + Calibration Loop + Minimal User Workflow

**Purpose**: Move from controlled mutation runtime (Phase 3) to real user-facing calibration workflow, while preserving Phase 3 mutation safety.

## What Phase 4 Includes

### P4-M1: Alter Dialogue Runtime
- Inject full alter.yaml into dialogue context
- Maintain persona consistency across turns
- Dialogue is read-only by default
- Dialogue output must not write active YAML

### P4-M2: Reality Score Form/API
- User submits reality score
- Score becomes calibration input
- Must be explicitly submitted by user
- No automatic score inference

### P4-M3: Drift Calculation
- Compute drift from reality score and expected validation signal
- No automatic regeneration
- Drift result is evidence only

### P4-M4: Calibration History Query
- Query previous scores, drift, and notes
- Read-only view over calibration records

### P4-M5: Rubric Delta Suggestion
- Detect repeated scoring mismatch
- Generate suggestion only
- Rubric cannot be auto-written

### P4-M6: Archive Mechanism
- Define archive trigger conditions
- Archive before major confirmed writes
- Rollback evidence required

### P4-M7: Checkpoint Regeneration Plan
- Triggered by high drift threshold (e.g. drift > 0.6)
- Produces regeneration plan / draft
- Does not directly overwrite active YAML

## Minimal Frontend Scope

Include minimal UI in Phase 4 only for:
- Alter Dialogue
- Reality Score Form
- Calibration History

Do NOT build:
- Broad product UI
- Branch map (unless explicitly approved later)
- Any frontend that triggers live execution

Frontend must call safe APIs only; no live execution trigger in frontend.

## What Phase 4 Excludes

- New branch discovery
- Automatic branch regeneration
- Snapshot schema rewrite
- Multi-user support
- Automatic rubric write
- Automatic archive write without explicit action
- LLM output directly writing active YAML
- Breaking Phase 3 active YAML structure
- Provider-backed autonomous execution without review
- Unreviewed semantic promotion

## Semantic Mutation Policy

Phase 4 may allow real semantic content to enter persistent state only through explicit gates.

First allowed semantic writes (limited to):
- `reality_score` records
- `calibration_history` records
- `rubric_delta_suggestion` records
- Archive/checkpoint metadata
- Explicitly saved dialogue session logs

Direct replacement of active branch/alter semantics remains blocked until a later explicitly approved slice.

No LLM output may jump directly to confirmed state.

## Required Promotion Model

```
LLM output or user input
  → schema validation
  → quality gate
  → generation_run or submission record
  → pending_review
  → explicit human confirmation
  → controlled write / controlled promotion path
  → evidence record
```

## Approval Model

- `pending_review → confirmed` requires explicit human action
- Token/hash may be required for persistent writes
- No silent confirmation
- No automatic active YAML mutation

## Rollback Model

- Before major confirmed semantic writes, archive current relevant state
- Archive must include enough data to restore
- Rollback path must be documented before write

## Audit Model

- Every LLM-assisted generation gets `generation_run` record
- Every persistent semantic write gets evidence
- Raw tokens are never stored
- Raw runtime logs are not committed

## Implementation Order

| Slice | Milestone | Description |
|-------|-----------|-------------|
| P4-000 | Scope and Boundary Plan | This document |
| P4-M1 | Alter Dialogue Runtime | Read-only dialogue with alter context |
| P4-M2 | Reality Score Form/API | User-submitted reality scores |
| P4-M3 | Drift Calculation | Compute drift from scores |
| P4-M4 | Calibration History Query | Read-only calibration view |
| P4-M5 | Rubric Delta Suggestion | Detect mismatch, suggest rubric |
| P4-M6 | Archive Mechanism | Archive before major writes |
| P4-M7 | Checkpoint Regeneration Plan | High-drift regeneration plan |

## Exit Gate

Phase 4 exits when ALL of the following are true:
- User can talk to an alter
- User can submit reality score
- System can compute drift
- System can show calibration history
- System can suggest rubric delta
- System can create archive/checkpoint plan
- No automatic semantic overwrite occurs
- All persistent writes are gated, audited, and test-covered

## Baseline

- Phase 3 sealed baseline: `86b75aa`
- Phase 3 closeout status: PASS_WITH_NOTES
- Phase 3 test count: 607
