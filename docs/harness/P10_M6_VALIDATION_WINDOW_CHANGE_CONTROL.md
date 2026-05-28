# P10-M6: Validation-Window Change Control

**Created:** 2026-05-28
**Status:** Active
**P6 State:** CODE_COMPLETE / VALIDATION_IN_PROGRESS / NOT_SEALED

## Purpose

During P6 validation, product behavior must remain stable. This document defines what changes are allowed during the validation window and how they must be logged.

## Rules

### Allowed Without Special Approval

- Redacted evidence docs (P10_M6_*_VALIDATION_EVIDENCE.md)
- Validation counters updates
- Run log entries
- Documentation clarifications that do not change product behavior
- Governance doc updates (PROJECT_BOARD, TASK_QUEUE, RUN_LOG, EVIDENCE_INDEX, CURRENT_SESSION_CONTEXT, START_HERE)

### Bugfixes Require Classification

| Severity | Definition | Allowed? | Requirements |
|----------|------------|----------|--------------|
| blocker | Cannot complete weekly note/review/score | Yes with approval | GPT/Charlie approval, logged |
| high | Risks corrupting validation evidence | Yes with approval | GPT/Charlie approval, logged |
| medium | Confusing but workaround exists | Defer until after P6 closeout | Unless materially affects evidence quality |
| low | Cosmetic or preference | Defer until after P6 closeout | No |

### Not Allowed During Validation

- New feature work (unless explicitly approved)
- Product code changes without classification and logging
- Provider configuration changes
- Schema changes that affect validation evidence format

## Change Log

All product code changes during validation must record:

| Date | Reason | Severity | Files Changed | Evidence Comparable | Window Status |
|------|--------|----------|---------------|---------------------|---------------|
| (none yet) | | | | | |

## Validation Window Status

- **Start date:** 2026-05-28
- **Current week:** 1 of 4
- **Required completion:** 4 weekly reviews, 4 calibration records, 1 pattern review, 21 days / 4 ISO weeks
- **P6 validated:** false
- **P6 sealed:** false

## Non-Countable Evidence (Reminder)

- P10-M2 does not count
- P10-M3 does not count
- P11 smoke does not count
- P11-PILOT-1 does not count
- Provider output does not count
- Synthetic data does not count

## Hard Boundaries

- No alters/current/** changes
- No alters/calibration/rubric.yaml changes
- No runtime records committed
- No raw weekly note/review content committed
- No provider secrets committed
- No real provider calls
- No provider output committed
- No P6 validated claim
- No P6 sealed claim
