# P11-M4: Gap Closure Plan

## Purpose

Turn P11-M1/M2/M3 analysis into a concrete implementation plan for P11-M5 and P11-M6. This is planning only — no code changes, no frontend implementation, no backend changes.

## Data Model/API Closure Review

| Feature | Existing API | Record Format Sufficient | Frontend-Only | New API Required | Migration Required | Personal Data Risk | Provider/Network Risk | Active YAML/Rubric Risk |
|---------|-------------|-------------------------|---------------|-----------------|-------------------|-------------------|----------------------|------------------------|
| CalibrationHistory detail view | GET /action-alignment/{score_id} | yes | yes | no | no | low | none | none |
| CalibrationHistory trend | GET /action-alignment/list | yes | yes | no | no | low | none | none |
| CalibrationHistory explanation | N/A (copy) | yes | yes | no | no | none | none | none |
| RealityScore history | GET /calibration-loop/history | yes | yes | no | no | low | none | none |
| RealityScore ↔ CalibrationHistory link | N/A (nav) | yes | yes | no | no | none | none | none |
| P6Progress user-friendly labels | GET /p6-data-retention/manifest | yes | yes | no | no | none | none | none |
| WeeklyReview Step 5 verdict explanation | N/A (copy) | yes | yes | no | no | none | none | none |
| WeeklyReview Step 3 dynamic alters | GET /alter-dialogue/alters | yes | yes | no | no | low | none | none |
| Pattern review frontend | GET /pattern-review/list, GET /pattern-review/{review_id}, POST /pattern-review/build | yes | yes | no | no | low | none | none |
| Behavior validation frontend | GET /behavior-validation/report, POST /behavior-validation/evaluate | yes | yes | no | no | low | none | none |
| Data management frontend | GET /p6-data-retention/manifest, POST /p6-data-retention/export, POST /p6-data-retention/delete, POST /p6-data-retention/archive | yes | yes | no | no | medium | none | none |

## Key Finding

All M5 and M6 features are **frontend-only changes**. Every required backend API already exists. No new API routes, no data model changes, no migrations. The gap is purely presentation and navigation.

## P11-M5 Implementation Batch 1

See `P11_M4_IMPLEMENTATION_BATCH_PLAN.md` for per-item detail.

### Items (5)

1. **CalibrationHistory detail/trend** — UX-001, UX-002, UX-003
2. **RealityScore history + CalibrationHistory connection** — UX-004
3. **P6Progress user-facing rewrite** — UX-007
4. **WeeklyReview Step 5 verdict explanation** — UX-006
5. **WeeklyReview Step 3 dynamic alter loading** (optional) — UX-005

### Backend Changes Required

**None.** All APIs exist and return sufficient data.

### Frontend Files Affected

- `apps/web/src/pages/CalibrationHistory.tsx` — detail view, trend, explanation
- `apps/web/src/pages/RealityScore.tsx` — history section, link to CalibrationHistory
- `apps/web/src/pages/P6Progress.tsx` — user-facing labels, progress counter
- `apps/web/src/pages/WeeklyReview.tsx` — Step 3 dynamic alters, Step 5 verdict explanation

## P11-M6 Implementation Batch 2

See `P11_M4_IMPLEMENTATION_BATCH_PLAN.md` for per-item detail.

### Items (3)

1. **Pattern review frontend** — G-009
2. **Behavior validation frontend** — G-010
3. **Data management visibility** — G-018

### Backend Changes Required

**None.** All APIs exist and return sufficient data.

### Frontend Files Affected

- `apps/web/src/pages/PatternReview.tsx` (new) — list, detail, build trigger
- `apps/web/src/pages/BehaviorValidation.tsx` (new) — report, evaluate, status
- `apps/web/src/pages/DataManagement.tsx` (new) — manifest, export, delete, archive controls

## Out of Scope (Deferred)

- AlterDialogue persistence (UX-010)
- RubricDelta cold-start improvements (UX-011)
- CheckpointPlan cold-start improvements (UX-012)
- GettingStarted interactivity (UX-008)
- SystemStatus developer label cleanup (UX-009)
- Self-deception challenge frontend (G-011)
- Alter recommendation frontend (G-012)
- Phase 3-6 route frontends (internal pipeline)
- Logs viewer frontend (CLI doctor sufficient)
