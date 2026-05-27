# P11-M4: Implementation Batch Plan

## P11-M5 Batch 1: Calibration/History Visibility + UX Polish

### Item 1: CalibrationHistory Detail View

- **Source UX gaps**: UX-001 (no detail drill-down), UX-003 (no score meaning explanation)
- **Affected files**: `apps/web/src/pages/CalibrationHistory.tsx`
- **Backend APIs to reuse**: `GET /action-alignment/{score_id}` (returns full score record), `GET /weekly-review/{session_id}` (returns linked review)
- **Data records to read**: `calibration_records/*.yaml` (via API)
- **Backend changes needed**: No
- **Expected behavior**: Click a score row → expanded detail panel showing: action_alignment_score value with scale explanation (0.0 = no alignment, 1.0 = full alignment), verdict label with human-readable meaning, verdict sentence (user's own words), evidence fields (one_action_evidence, etc.), linked weekly review excerpt, date/timestamp
- **Tests required**: Frontend build passes, detail panel renders on click, explanation text present
- **Acceptance criteria**: User can click any score and understand what it means without external docs
- **Out of scope**: Drift visualization, comparison view, export

### Item 2: CalibrationHistory Trend Indicator

- **Source UX gaps**: UX-002 (no trend visualization)
- **Affected files**: `apps/web/src/pages/CalibrationHistory.tsx`
- **Backend APIs to reuse**: `GET /action-alignment/list` (returns all scores sorted by date)
- **Data records to read**: `calibration_records/*.yaml` (via API)
- **Backend changes needed**: No
- **Expected behavior**: Action alignment score list shows trend arrow (up/down/stable) comparing most recent to previous score. If only one score exists, show "first score" indicator. Score list sorted by date, not ID.
- **Tests required**: Frontend build passes, trend arrow renders correctly for improving/declining/stable/first-score cases
- **Acceptance criteria**: User can see at a glance whether their alignment is improving
- **Out of scope**: Sparkline chart, week-over-week comparison, drift visualization

### Item 3: CalibrationHistory Score Explanation

- **Source UX gaps**: UX-003 (no explanation of score meaning or relationship between record types)
- **Affected files**: `apps/web/src/pages/CalibrationHistory.tsx`
- **Backend APIs to reuse**: None (copy/UI only)
- **Data records to read**: None
- **Backend changes needed**: No
- **Expected behavior**: Page header or info section explains: what action alignment score means, what verdict labels mean (aligned_progress, noisy_progress, etc.), relationship between weekly reviews and calibration records, how scores relate to reality scores
- **Tests required**: Frontend build passes, explanation text renders
- **Acceptance criteria**: New user can understand the page without reading external docs
- **Out of scope**: Interactive tutorial, guided walkthrough

### Item 4: RealityScore History + CalibrationHistory Connection

- **Source UX gaps**: UX-004 (no link to CalibrationHistory, no history of submitted scores)
- **Affected files**: `apps/web/src/pages/RealityScore.tsx`
- **Backend APIs to reuse**: `GET /calibration-loop/history` (returns calibration history with drift), `GET /action-alignment/list` (returns action alignment scores)
- **Data records to read**: `calibration_records/*.yaml` (via API)
- **Backend changes needed**: No
- **Expected behavior**: RealityScore page shows: recent calibration history (last 5 scores), link to full CalibrationHistory page, explanation of how reality scores relate to calibration
- **Tests required**: Frontend build passes, history section renders, link to CalibrationHistory works
- **Acceptance criteria**: User can see recent scores without leaving the page, and navigate to full history
- **Out of scope**: Cross-page data sync, real-time updates

### Item 5: P6Progress User-Facing Rewrite

- **Source UX gaps**: UX-007 (developer-facing labels, no progress counter, no "what next")
- **Affected files**: `apps/web/src/pages/P6Progress.tsx`
- **Backend APIs to reuse**: `GET /p6-data-retention/manifest` (returns record counts), `GET /weekly-review/list` (returns review count), `GET /action-alignment/list` (returns score count)
- **Data records to read**: `weekly_reviews/*.yaml`, `calibration_records/*.yaml` (via API counts)
- **Backend changes needed**: No
- **Expected behavior**: Replace CODE_COMPLETE/NOT_VALIDATED/NOT_SEALED labels with user-facing: "Weekly reviews completed: N", "Alignment scores recorded: N", "Validation status: Not started (requires 4 weekly reviews over 21+ days)". Show next-step guidance: "Complete weekly reviews to build validation evidence"
- **Tests required**: Frontend build passes, user-facing labels render, P6 false flags remain correct
- **Acceptance criteria**: User understands their progress and what to do next without developer knowledge
- **Out of scope**: Validation start button, progress bar animation

### Item 6: WeeklyReview Step 5 Verdict Explanation

- **Source UX gaps**: UX-006 (verdict labels need user-facing explanation)
- **Affected files**: `apps/web/src/pages/WeeklyReview.tsx`
- **Backend APIs to reuse**: None (copy/UI only)
- **Data records to read**: None
- **Backend changes needed**: No
- **Expected behavior**: Step 5 verdict selector shows human-readable descriptions: "Aligned Progress — my actions matched my stated direction", "Noisy Progress — I made progress but not in my intended direction", "Drift — my actions moved away from my goals", "Stall — I did not make meaningful progress"
- **Tests required**: Frontend build passes, verdict descriptions render
- **Acceptance criteria**: User can select a verdict and understand what it means
- **Out of scope**: Verdict auto-suggestion, AI-assisted verdict selection

### Item 7 (Optional): WeeklyReview Step 3 Dynamic Alter Loading

- **Source UX gaps**: UX-005 (Step 3 hardcoded alters)
- **Affected files**: `apps/web/src/pages/WeeklyReview.tsx`
- **Backend APIs to reuse**: `GET /alter-dialogue/alters` (returns list of active alters)
- **Data records to read**: alter YAML files (via API)
- **Backend changes needed**: No
- **Expected behavior**: Step 3 alter dropdown loads from API instead of hardcoded alter_A-D options
- **Tests required**: Frontend build passes, dropdown shows API-loaded alters
- **Acceptance criteria**: Alter list matches what the backend reports
- **Out of scope**: Alter creation UI, alter detail view

---

## P11-M6 Batch 2: P6 Readiness Frontends + Data Management

### Item 1: Pattern Review Frontend

- **Source gaps**: G-009 (pattern review — medium severity, P6-reconsideration blocker)
- **Affected files**: `apps/web/src/pages/PatternReview.tsx` (new), `apps/web/src/App.tsx` (nav)
- **Backend APIs to reuse**: `GET /pattern-review/list`, `GET /pattern-review/{review_id}`, `POST /pattern-review/build`
- **Data records to read/create**: `pattern_reviews/*.yaml` (via API)
- **Backend changes needed**: No
- **Safety boundaries**: build triggers pattern detection on existing records, no provider calls, no active YAML mutation
- **Tests required**: Frontend build passes, list view renders, detail view renders, build button triggers and shows result
- **Acceptance criteria**: User can list past pattern reviews, view a detail report, and trigger a new pattern build. UI does NOT claim validation is complete.
- **Out of scope**: Pattern visualization, pattern comparison, pattern export

### Item 2: Behavior Validation Frontend

- **Source gaps**: G-010 (behavior validation — high severity, P6-reconsideration blocker)
- **Affected files**: `apps/web/src/pages/BehaviorValidation.tsx` (new), `apps/web/src/App.tsx` (nav)
- **Backend APIs to reuse**: `GET /behavior-validation/report`, `POST /behavior-validation/evaluate`
- **Data records to read/create**: `behavior_validation/*.yaml`, `weekly_reviews/*.yaml`, `calibration_records/*.yaml`, `pattern_reviews/*.yaml` (all via API)
- **Backend changes needed**: No
- **Safety boundaries**: evaluate checks persisted evidence (weekly reviews, calibration records, pattern reviews) and 4-week window. Does NOT claim validation complete unless backend confirms. No provider output used as evidence.
- **Tests required**: Frontend build passes, report view renders, evaluate triggers and shows result, UI shows "validation not started" when no evidence
- **Acceptance criteria**: User can view validation status and trigger evaluation. UI does NOT claim P6 is validated. P6 false flags remain correct.
- **Out of scope**: Validation start button, validation seal, validation progress animation

### Item 3: Data Management Visibility

- **Source gaps**: G-018 (data export/delete/archive — no frontend)
- **Affected files**: `apps/web/src/pages/DataManagement.tsx` (new), `apps/web/src/App.tsx` (nav)
- **Backend APIs to reuse**: `GET /p6-data-retention/manifest`, `POST /p6-data-retention/export`, `POST /p6-data-retention/delete`, `POST /p6-data-retention/archive`
- **Data records to read/create**: All product data (via manifest), exports, archives (via API)
- **Backend changes needed**: No
- **Safety boundaries**: Export creates read-only archive. Delete requires explicit confirmation. Archive is explicit-only copy. No provider output in exports.
- **Tests required**: Frontend build passes, manifest shows record counts, export button works, delete confirmation dialog works, archive button works
- **Acceptance criteria**: User can see what data exists, export it, archive it, or delete specific records with explicit confirmation. No accidental data loss.
- **Out of scope**: Bulk operations, import, data migration, cloud backup
