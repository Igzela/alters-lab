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
 P1-004 | Controlled Snapshot YAML Write | done |
 P1-005 | Controlled Branches YAML Write | done |
 P1-006 | Controlled Alter YAML Write | done |
| P1-007 | Value Alignment Controlled YAML Write | done |
 P1-008 | Controlled Dialogue YAML Write | done |
 P1-009 | Reality Trace / Weekly Evidence Controlled Write | done |
 P1-010 | State Reconciliation + Active YAML Schema Normalization | done |
| P1-011 | Governance Truth Repair + Day 30 Demo Definition | done |
| P1-012 | Day 30 Evidence Harness + Schema Alignment | done |
| P1-013 | Phase 1 Closeout / Day 30 Evidence Review | **blocked** |

## Phase 1 Sealed Baseline

Phase 1 Final Gate: **PASS**
- Day 14 gate: PASSED
- Day 30 gate: PASSED
- 62 tests passing
- 9 active YAML artifacts validated
- Commit: 9a59317 pushed to main

## Phase 2 — Read-Only Runtime Foundation

| ID | Title | Status |
|----|-------|--------|
| P2-001 | Sealed Baseline Verification + Active YAML Loader | **done** |
| P2-002 | Active YAML Chain Validator CLI | **done** |
| P2-003 | Read-only Cycle Summary API | **done** |
| P2-004 | Read-only Evidence Report API | **done** |
| P2-005 | Phase 2 Closeout / Read-only Runtime Review | **done** |

## Phase 2 Sealed Baseline

Phase 2 Final Gate: **PASS**
- 110 tests passing
- 9 active YAML artifacts validated (PASS, selected_branch=branch_D)
- API surface: 3 routers (snapshot-intake, cycle-summary, evidence-reports), all read-only on cycle-summary and evidence
- No forbidden components (provider, database, frontend, runtime modules)
- Commit: 272b39f on main (P2-004)
- Closeout report: `docs/harness/PHASE2_CLOSEOUT_REPORT.md`

## Quality Gates

**day_14 gate**: "FastAPI backend can run Snapshot Intake contract and tests." — **COMPLETED** (P1-001 through P1-003 passed)

 **day_30 gate**: "Complete CYCLE-001 flow can run through at least one real snapshot, branches, alters, dialogue/value alignment, and reality trace." — **PASSED** (P1-012 evidence harness confirms 9-step validation; Day 30 evidence review pending in P1-013)

## Notes

- COC-001 is complete (repo skeleton). All COC-* tasks after 001 are paused/retired.
- COC-002 through COC-008 are retired. The content calibration direction has been replaced by Alters System.
- All new work uses ALT-* task IDs.
- ALT-001 through ALT-008 are complete. Phase 0 workspace final gate review passed.
- CYCLE-001A (First real Snapshot Intake) is ready-with-approval — awaiting human decision to begin.
- P1-001 complete. Phase 1 has started with backend foundation.
- P1-002 complete. Snapshot Intake API endpoints exposed via in-memory FastAPI backend. Day 14 gate moved closer but YAML persistence remains future slice.
- P1-003 complete. Snapshot YAML persistence and export gate implemented. Day 14 gate passed.
 P1-004 through P1-009 complete. Controlled Snapshot YAML Write, Controlled Branches YAML Write, Controlled Alter YAML Write, Controlled Value Alignment YAML Write, Controlled Dialogue YAML Write, and Reality Trace / Weekly Evidence Controlled Write (not backend runtime implementations). See DECISION_RECORD.md.
 P1-010 complete. State Reconciliation + Active YAML Schema Normalization adopted. See DECISION_RECORD.md for rationale.
- P1-011 complete. Governance Truth Repair + Day 30 Demo Definition — all governance docs aligned with current phase state.
- P1-012 complete. Day 30 Evidence Harness + Schema Alignment — 9-step evidence schema validated, harness regenerated.
- Day 14 gate completed. Day 30 gate passed (P1-012). Phase 1 closeout pending in P1-013.
