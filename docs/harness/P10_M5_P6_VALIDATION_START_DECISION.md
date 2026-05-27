# P10-M5: P6 Validation Start Decision Gate

## Current State

| Item | Status |
|------|--------|
| P10-M2 | done — first real weekly note ingested via packaged app |
| P10-M3 | done — first real weekly review session completed via packaged app |
| P10-M4 | done — friction log: 0 blocker, 3 low-severity accepted_no_fix |
| P6 | CODE_COMPLETE / NOT_VALIDATED / NOT_SEALED |

## Decision Options

| Option | Meaning |
|--------|---------|
| **A. START_P6_VALIDATION_NOW** | Begin the 4-week P6 validation window. P6 state becomes CODE_COMPLETE / VALIDATION_IN_PROGRESS / NOT_SEALED. |
| **B. DEFER_P6_VALIDATION** | Delay P6 validation start. P6 remains CODE_COMPLETE / NOT_VALIDATED / NOT_SEALED. Revisit later. |
| **C. BLOCKED_BY_NEW_FRICTION** | New blocker friction prevents starting. P6 remains CODE_COMPLETE / NOT_VALIDATED / NOT_SEALED. Blocker documented. |

## GPT Recommendation

**START_P6_VALIDATION_NOW**

Reason:
- Packaged app cutover complete (P10-M1)
- First real weekly note ingested (P10-M2)
- First real weekly review completed (P10-M3)
- Action alignment score created: 0.75 aligned_progress (P10-M3)
- P10-M4 found 0 blocker friction and 0 must-fix-before-P6-start
- P6 validation start conditions are satisfied

## Preconditions Satisfied

- [x] Explicit weekly note evidence exists (P10_M2_REAL_WEEKLY_NOTE_INGEST_EVIDENCE.md)
- [x] Real weekly review evidence exists (P10_M3_REAL_WEEKLY_REVIEW_EVIDENCE.md)
- [x] Action alignment score exists (0.75, recorded in P10-M3 evidence)
- [x] No blocker friction (P10_M4: 0 blocker)
- [x] Synthetic evidence excluded
- [x] Provider output excluded

## What START_P6_VALIDATION_NOW Means

If Charlie chooses **START_P6_VALIDATION_NOW**:

- P6 state becomes: **CODE_COMPLETE / VALIDATION_IN_PROGRESS / NOT_SEALED**
- This does **NOT** mean P6 is validated
- This does **NOT** mean P6 is sealed
- The 4-week validation clock starts

## Completion Requirements (if START)

For P6 to complete validation, all of the following must be met:

| Requirement | Target |
|-------------|--------|
| Real weekly reviews | 4 |
| Calibration records | 4 |
| Action alignment scores | 4 |
| Pattern reviews | 1 |
| Time window | 21 days / 4 ISO weeks |
| Synthetic evidence | excluded |
| Provider output as evidence | excluded |
| Closeout decision | explicit human/GPT |

## Required Action

**Charlie must explicitly reply with one of:**
- `START_P6_VALIDATION_NOW`
- `DEFER_P6_VALIDATION`
- `BLOCKED_BY_NEW_FRICTION`

This decision cannot be made by Codex or GPT alone. It requires explicit human authorization.
