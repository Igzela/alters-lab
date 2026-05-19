# Project Board

## Task States

```
todo → ready → running → review → done/failed
```

## Execution Slices

| ID | Title | Status |
|----|-------|--------|
| COC-001 | Repo skeleton + governance docs (content calibration) | done |
| COC-002 | Backend schema definitions (content calibration) | **paused** |
| ALT-001 | Reset project direction to Alters System + Phase 0 workspace | done |
| ALT-002 | Snapshot intake workflow | done |
| ALT-003 | Branch discovery engine | done |
| ALT-004 | Alter generation | done |
| ALT-005 | Dialogue engine | done |
| ALT-006 | Value alignment evaluator | done |
| ALT-007 | Calibration system + rubric | done |
| ALT-008 | Archive system | done |
| CYCLE-001A | First real Snapshot Intake cycle | ready-with-approval |

## Phase 1 — Controlled Implementation

| ID | Title | Status |
|----|-------|--------|
| P1-001 | Backend Foundation + Snapshot Intake Contract | done |
| P1-002 | Snapshot Intake API Endpoints | done |
| P1-003 | Snapshot YAML Persistence / Export Gate | done |
| P1-004 | Branch Discovery Backend Service + API | done |
| P1-005 | Alter Generation Backend Service + API | done |
| P1-006 | Dialogue Engine Backend Service + API | done |
| P1-007 | Value Alignment Backend Service + API | done |
| P1-008 | Calibration Backend Service + API | done |
| P1-009 | Archive Backend Service + API | done |
| P1-010 | Flat Active Alter Schema (source_refs, quality_status) | done |
| P1-011 | End-to-End Integration + CYCLE-001A Trigger | **blocked** |

## Quality Gates

**day_14 gate**: "FastAPI backend can run Snapshot Intake contract and tests." — **COMPLETED** (P1-001 through P1-003 passed)

**day_30 gate**: "Complete CYCLE-001 flow can run through at least one real snapshot, branches, alters, dialogue/value alignment, and calibration template." — **PENDING** (P1-004 through P1-010 complete; integration pending in P1-011)

## Notes

- COC-001 is complete (repo skeleton). All COC-* tasks after 001 are paused/retired.
- COC-002 through COC-008 are retired. The content calibration direction has been replaced by Alters System.
- All new work uses ALT-* task IDs.
- ALT-001 through ALT-008 are complete. Phase 0 workspace final gate review passed.
- CYCLE-001A (First real Snapshot Intake) is ready-with-approval — awaiting human decision to begin.
- P1-001 complete. Phase 1 has started with backend foundation.
- P1-002 complete. Snapshot Intake API endpoints exposed via in-memory FastAPI backend. Day 14 gate moved closer but YAML persistence remains future slice.
- P1-003 complete. Snapshot YAML persistence and export gate implemented. Day 14 gate passed.
- P1-004 through P1-009 complete. Branch Discovery, Alter Generation, Dialogue, Value Alignment, Calibration, and Archive backend services and API endpoints implemented.
- P1-010 complete. Flat active Alter schema adopted with source_refs and quality_status fields. See DECISION_RECORD.md for rationale.
- P1-011 blocked. End-to-end integration and CYCLE-001A trigger pending — waiting on governance docs alignment (this update).
- Day 14 gate completed. Day 30 gate pending — requires P1-011 integration to pass.
