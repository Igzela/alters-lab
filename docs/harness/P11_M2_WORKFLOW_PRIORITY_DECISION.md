# P11-M2: Workflow Priority Decision

## Decision

**Do not try to complete every historical Phase 3-6 route.** Focus on workflows that make the app normally usable and P6-ready.

## Priority Recommendation

### P11-M3 Focus: Calibration / History Visibility (Analysis Only)

**Rationale**: The CalibrationHistory page exists but only shows a list. Users need to see individual calibration records, trend data, and understand their calibration trajectory. This is the most visible gap for a user who has completed a few weekly reviews.

**Scope** (analysis only — no implementation):
- UX gap analysis for calibration/history visibility
- RealityScore user experience analysis
- Normal-use blocker identification
- No code changes, no frontend implementation

**What NOT to do in P11-M3**:
- Do not implement any frontend changes
- Do not build frontend for Phase 3-6 controlled write routes
- Do not add new API routes

### P11-M4 Focus: Gap Closure Plan

**Rationale**: After M3 identifies UX gaps, M4 creates the closure plan for what needs to be built.

**Scope** (planning only — no implementation):
- Data model/API/frontend gap closure plan
- Phase M5/M6 implementation batching
- No code changes

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

| Phase | Focus | Type | Files to Create |
|-------|-------|------|-----------------|
| P11-M3 | Calibration / history visibility, UX gaps, normal-use blockers | analysis only | UX gap analysis, frontend gap list |
| P11-M4 | Gap closure plan | planning only | Implementation plan for M5/M6 |
| P11-M5 | Product completion batch 1 | implementation | CalibrationHistory detail, RealityScore improvements |
| P11-M6 | Product completion batch 2 | implementation | Pattern review frontend, behavior validation frontend, data management |
| P11-M7 | Product completeness smoke and closeout | verification | Final verification |
