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
| P1-004 | Controlled Snapshot YAML Write | done |
| P1-005 | Controlled Branches YAML Write | done |
| P1-006 | Controlled Alter YAML Write | done |
| P1-007 | Value Alignment Controlled YAML Write | done |
| P1-008 | Controlled Dialogue YAML Write | done |
| P1-009 | Reality Trace / Weekly Evidence Controlled Write | done |
| P1-010 | State Reconciliation + Active YAML Schema Normalization | done |
| P1-011 | Governance Truth Repair + Day 30 Demo Definition | done |
| P1-012 | Day 30 Evidence Harness + Schema Alignment | done |
| P1-013 | Phase 1 Closeout / Day 30 Evidence Review | **done** |

## Phase 5 — Local Product MVP

| ID | Title | Status |
|----|-------|--------|
| P5-000 | Productization / Provider / Frontend Boundary Plan | **done** |
| P5-M1 | API Product Surface Hardening | **done** |
| P5-M2 | Provider Gateway Boundary | **done** |
| P5-M3 | Provider-backed Alter Dialogue | **done** |
| P5-M4 | Minimal Frontend MVP | **done** |
| P5-M5 | Durable Storage Boundary | **done** |
| P5-M6 | User Workflow Integration | **done** |
| P5-M7 | Safety Review and Product Closeout | **done** |
| P5-M8 | Local Release Candidate | **done** |
| P5-CLOSEOUT | Phase 5 Closeout | **done** |
| P6-000 | Personal Long-Term Use Hardening Plan | **done** |

## Phase 6 — Personal Long-Term Use Hardening

| ID | Title | Status |
|----|-------|--------|
| P6-000 | Personal Long-Term Use Hardening Plan | **done** |
| P6-CODE-COMPLETE | P6 Runtime Code Complete | **accepted** |
| P6-ENDGAME | Real-Use Validation Orchestration | **running** |
| P6-M1 | Obsidian Weekly Note Ingest | **code_complete_accepted** |
| P6-M2 | Weekly Review Session Runtime | **code_complete_accepted** |
| P6-M3 | Action Alignment Scoring | **code_complete_accepted** |
| P6-M4 | Self-Deception and Challenge Layer | **code_complete_accepted** |
| P6-M5 | Alter Recommendation Engine | **code_complete_accepted** |
| P6-M6 | Reminder / Skip-with-Reason Flow | **code_complete_accepted** |
| P6-M7 | 4-Week Pattern Review | **code_complete_accepted** |
| P6-M8 | Data Retention / Export / Delete | **code_complete_accepted** |
| P6-M9 | Real Provider Optional Enablement | **code_complete_accepted** |
| P6-M10 | Behavior Validation Gate | **implemented_waiting_real_use** |
| P6-M11 | P6 Closeout | **implemented_blocked_by_behavior_validation** |
| P6-BEHAVIOR-VALIDATION | Real 4-week behavior validation | **blocked_by_real_use_window** |
| P6-CLOSEOUT | Final Phase 6 closeout | **blocked** |

P6 state: **CODE_COMPLETE / P6_SKIPPED_VALIDATION** — human decision to skip 4-week real-use validation. P6 code-complete accepted as-is.

## Phase 7 — Local App Distribution / Debian Package / Independent Desktop Runtime

| ID | Title | Status |
|----|-------|--------|
| P7-000 | Local App Distribution Boundary Plan | **done** |
| P7-M1 | Runtime Layout Externalization | **done** |
| P7-M2 | Unified Local Server | **done** |
| P7-M3 | CLI Launcher | **done** |
| P7-M4 | Provider Configuration UI/API | **done** |
| P7-M5 | Debian Package Build | **done** |
| P7-M6 | Desktop Integration | **done** |
| P7-M7 | Upgrade / Uninstall / Data Safety | **done** |
| P7-M8 | Local App Release Candidate | **done** |
| P7-M9 | P7 Closeout | **done** |

## Phase 7 Sealed Baseline

P7 Final Gate: **LOCAL_APP_RELEASE_CANDIDATE**
- Backend tests: 949 passed
- Frontend build: PASS
- Debian package build: PASS
- Package safety inspection: PASS
- Package-context smoke: PASS
- Closeout report: `docs/harness/P7_CLOSEOUT_REPORT.md`
- P6: CODE_COMPLETE / P6_SKIPPED_VALIDATION
- P8: PASS (P8-000 through P8-M4 complete)

## Phase 7 Repair / Usability Follow-up

| ID | Title | Status |
|----|-------|--------|
| P7-R1 | Complete P6 Frontend Usability Layer | **done** |
| DOCS-R1 | New Session Bootstrap Docs | **done** |

## Phase 8 — Real Provider Integration & End-to-End Validation

| ID | Title | Status |
|----|-------|--------|
| P8-000 | Real Provider Integration & E2E Boundary Plan | **done** |
| P8-M1 | Real Provider Integration | **done** |
| P8-M2 | End-to-End Workflow Validation | **done** |
| P8-M3 | Configuration & Documentation | **done** |
| P8-M4 | P8 Closeout | **done** |

P6 status: **P6_SKIPPED_VALIDATION** — human decision to skip 4-week real-use validation. P6 code-complete accepted as-is.
P8 status: **PASS** — all P8 milestones complete, sealed baseline established.

## Phase 8 Sealed Baseline

P8 Final Gate: **PASS**
- Backend tests: 1004 passed
- Real provider integration: PASS
- E2E validation: PASS (27 tests)
- Documentation: PASS (README, PROVIDER_CONFIGURATION.md, USER_GUIDE.md)
- P6 status: P6_SKIPPED_VALIDATION
- P7 status: LOCAL_APP_RELEASE_CANDIDATE
- Closeout report: `docs/harness/P8_CLOSEOUT_REPORT.md`

## Phase 5 Sealed Baseline

Phase 5 Final Gate: **PASS**
- 802 tests passing
- 17 new API routes added
- Frontend MVP (Vite + React + TypeScript)
- Provider gateway (mock default)
- No active YAML modified
- No secrets committed
- No database migration
- Closeout report: `docs/harness/PHASE5_CLOSEOUT_REPORT.md`

## Phase 4 Sealed Baseline

Phase 4 Final Gate: **PASS**
- P4-FINAL accepted
- Closeout status: PASS
- Commit: 2ae89a9d7d81d451e3efdc40d9054b13a9e50cb7
- Closeout report: `docs/harness/PHASE4_CLOSEOUT_REPORT.md`

## Phase 3 Sealed Baseline

Phase 3 Final Gate: **SEALED_WITH_NOTES**
- Closeout status: PASS_WITH_NOTES
- 607 tests passing
- Sealed baseline commit: 86b75aa
- Closeout report: `docs/harness/PHASE3_CLOSEOUT_REPORT.md`
- P4-000 scope and boundary plan complete
- P4-CAL-LOOP-MVP complete pending GPT verdict

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
| P2-005R | Phase 2 Closeout Correction — governance and API contract gaps | **done** |

## Phase 2 Sealed Baseline

Phase 2 Final Gate: **PASS**
- 118 tests passing
- 9 active YAML artifacts validated (PASS, selected_branch=branch_D)
- API surface: 3 routers (snapshot-intake, cycle-summary, evidence-reports), all read-only on cycle-summary and evidence
- No forbidden components (provider, database, frontend, runtime modules)
- Commit: 38ffcc2 (Phase 2 sealed baseline)
- Closeout report: `docs/harness/PHASE2_CLOSEOUT_REPORT.md`

## Phase 3 — Controlled Mutation

| ID | Title | Status |
|----|-------|--------|
| P3-000 | Phase 3 Scope and Boundary Plan | **done** |
| P3-001 | Controlled Snapshot Write API | **done** |
| P3-001R | Controlled Snapshot Write API Contract Repair | **done** |
| P3-001R2 | Controlled Snapshot Write API Final Contract Repair | **done** |
| P3-001R3 | Audit Evidence Cleanup | **done** |
| P3-002 | Controlled Branches Write API | **done** |
| P3-003 | Controlled Alter Write API | **done** |
| P3-M1 | Controlled YAML Write Surface Expansion | **done** |
| P3-M1R | Controlled Write Surface Contract Hardening | **done** |
| P3-M2 | Controlled Generation Draft Runtime | **done** |
| P3-M2R | Real Loader Integration Repair | **done** |
| P3-M3 | Draft Review and Promotion Boundary | **done** |
| P3-M3R | Promotion Package Contract Hardening | **done** |
| P3-M3R2 | Promotion Payload Exactness Repair | **done** |
| P3-M4 | Controlled Active Promotion Orchestration Plan | **done** |
| P3-M5 | Controlled Promotion Execution Gate | **done** |
| P3-M6 | Controlled Promotion Live Execution | **done** |
| P3-M6R | Live Executor Persist Signature Repair | **done** |
| P3-M6R2 | Raw Dict Re-persist Preserves Extras Without Weakening API Schemas | **done** |
| P3-M7 | First Human-Approved Live Promotion Run | **done** |
| P3-M8 | Phase 3 Controlled Mutation Closeout Gate | **done** |
| P3-M8R | Closeout API Read-Only Repair | **done** |
| P3-M8R2 | Closeout Evidence Truth Repair | **done** |
| P4-000 | Phase 4 Scope and Boundary Plan | **done** |
| P4-M1 | Alter Dialogue Runtime | **done** |
| P4-M1R | Dialogue Contract Hardening | **done** |
| P4-M2 | Reality Score Form/API | **done** |
| P4-M3 | Drift Calculation | **done** |
| P4-M4 | Calibration History Query | **done** |
| P4-M5 | Rubric Delta Suggestion | **done** |
| P4-M6 | Archive Mechanism | **done** |
| P4-M7 | Checkpoint Regeneration Plan | **done** |
| P4-CLOSEOUT | Phase 4 Closeout | **done** |
| P5-000 | Future Productization / Provider Boundary Plan | **done** |

## Quality Gates

**day_14 gate**: "FastAPI backend can run Snapshot Intake contract and tests." — **COMPLETED** (P1-001 through P1-003 passed)

 **day_30 gate**: "Complete CYCLE-001 flow can run through at least one real snapshot, branches, alters, dialogue/value alignment, and reality trace." — **PASSED** (P1-012 evidence harness confirms 9-step validation; Day 30 evidence review completed (P1-012R, P1-013 sealed))

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
- Day 14 gate completed. Day 30 gate passed (P1-012). Phase 1 sealed (P1-013 done).
- P3-M8R2 complete. Closeout evidence truth repair — distinguishes tracked vs untracked audit files. Phase 3 sealed baseline established.
- P4-000 complete. Phase 4 scope and boundary plan defined.
- P4-M1 complete. Read-only alter dialogue runtime — no provider, no active YAML write, 656 tests passing.
- P4-CAL-LOOP-MVP complete pending GPT verdict. P4-M1R hardens full alter YAML injection. P4-M2/M3/M4 add explicit reality score records, evidence-only drift, and read-only calibration history. No provider, frontend, database, active YAML mutation, rubric mutation, archive, promotion, or regeneration trigger.
- P4-FINAL complete. P4-M5 rubric delta suggestions are suggestion-only. P4-M6 archive creation is explicit-only copy packaging. P4-M7 checkpoint regeneration is plan-only. Phase 4 closeout establishes a backend calibration loop sealed candidate. P5-000 remains blocked pending GPT/human review.
- P5-FULL complete. Local product MVP: provider gateway (mock default), provider-backed dialogue, minimal frontend (Vite+React), storage boundary (YAML default), user workflow integration, phase 5 closeout PASS. 802 tests passing. 17 new API routes. No active YAML modified. No secrets committed. No database migration. P6-000 complete. P6 is personal long-term use hardening, not public productization. P6 success = behavior change after 4-week validation window. P6-M1 ready_with_approval. P7-000 blocked.
- P6 runtime code complete accepted and merged to main at cdf4d4e6bf20c3ed160c429c1520dd1ec74917e1. P6-M1 through P6-M11 backend routes/services/schemas are implemented. P6-CODE-COMPLETE-R1 fixed the fake-ID validation blocker. 840 backend tests passing. P6 behavior validation SKIPPED by explicit human decision (P6_SKIPPED_VALIDATION). P6 code-complete accepted as-is. See `docs/harness/P6_SKIP_DECISION.md`.
- P8 complete. Real Provider Integration & E2E Validation sealed baseline: 1004 backend tests, 27 E2E tests, real provider integration PASS. P8 closeout report at `docs/harness/P8_CLOSEOUT_REPORT.md`.
