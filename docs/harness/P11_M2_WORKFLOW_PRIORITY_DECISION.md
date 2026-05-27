# P11-M2: Workflow Priority Decision

## Decision

**Do not try to complete every historical Phase 3-6 route.** Focus on workflows that make the app normally usable and P6-ready.

## Priority Recommendation

### P11-M3 Focus: Calibration / History Visibility

**Rationale**: The CalibrationHistory page exists but only shows a list. Users need to see individual calibration records, trend data, and understand their calibration trajectory. This is the most visible gap for a user who has completed a few weekly reviews.

**Scope**:
- CalibrationHistory detail view (click into a record)
- RealityScore page improvements (show recent scores, drift indicator)
- Keep existing backend routes, add frontend read-only views

**What NOT to do in P11-M3**:
- Do not build frontend for Phase 3-6 controlled write routes (snapshot intake, branches, alters, generation, draft review, promotion)
- These are internal pipeline routes, not user-facing workflows
- Users don't need to interact with snapshot intake, branch persistence, or alter persistence directly

### P11-M4 Focus: Validation Readiness Frontends

**Rationale**: These workflows are needed before P6 validation can be reconsidered. Backend exists, but no frontend visibility.

**Scope**:
- Pattern review frontend (view 4-week patterns)
- Behavior validation frontend (view validation reports)
- Data export/delete/archive frontend (data management visibility)

### Defer

- Alter dialogue persistence (not needed for normal weekly use)
- RubricDelta / CheckpointPlan (cold start, no real data)
- Logs viewer (CLI doctor sufficient)
- Provider live setup (user-initiated, not blocking)
- Self-deception challenge frontend (supporting evidence only)
- Alter recommendation frontend (supporting evidence only)

## Decision Rationale

The app's primary value is the **weekly review loop**: ingest note → review → score alignment. This works end-to-end. The next priority is making the **calibration trajectory visible** so users can see their progress over time. After that, the validation-readiness frontends (pattern review, behavior validation) unlock P6 reconsideration.

Historical Phase 3-6 routes (snapshot intake, branches, alter persistence, generation drafts, draft review, promotion orchestration, promotion execution, live execution) are **internal pipeline routes** that served the controlled-write development process. They are not user-facing workflows. Building frontend for them would be over-engineering for a personal-use app.

## Recommended P11-M3/P11-M4 Split

| Phase | Focus | Files to Create |
|-------|-------|-----------------|
| P11-M3 | Calibration / history visibility | UX gap analysis, frontend gap list |
| P11-M4 | Gap closure plan | Implementation plan for M5/M6 |
| P11-M5 | Product completion batch 1 | CalibrationHistory detail, RealityScore improvements |
| P11-M6 | Product completion batch 2 | Pattern review frontend, behavior validation frontend, data management |
| P11-M7 | Product completeness smoke and closeout | Final verification |
