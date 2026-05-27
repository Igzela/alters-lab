# P11-M3: UX Gaps and Normal-Use Blockers

## Normal-Use Journey Audit

| Step | Current UX Path | What User Sees | What User Can Do | Missing/Confusing | Severity | Recommendation |
|------|----------------|----------------|------------------|-------------------|----------|----------------|
| 1. Install package | dpkg -i | System package installed | N/A | Nothing — works cleanly | none | keep |
| 2. Start/open app | CLI start/open or auto-opens browser | Browser opens to http://127.0.0.1:18790 | See SystemStatus page | Nothing — works cleanly | none | keep |
| 3. First run / getting started | Click "Getting Started" nav | Static checklist with 6 items | Read checklist | Checklist is static text, no interactivity, no progress tracking | low | docs_only |
| 4. Confirm provider disabled | ProviderSettings page | Shows "disabled" mode, config/status | Read status | Nothing — clear | none | keep |
| 5. Switch to mock (optional) | ProviderSettings: select mock, save, test | Config saved, test result shown | Switch mode, test connectivity | Nothing — works end-to-end | none | keep |
| 6. Ingest weekly note | WeeklyReview Step 1: paste note, click ingest | Template button, textarea, ingest button | Paste note, use template, ingest | Template is pre-filled but user must click "Use template" first. No indication of what fields will be extracted. | low | UX_copy |
| 7. Complete weekly review | WeeklyReview Steps 2-5: review extracted → start → complete → score | 6-step wizard with step buttons | Navigate steps, fill fields, submit | Step 3 has hardcoded alter options (alter_A-D) not loaded from API. Step 4 requires review_note + primary_next_correction but no guidance on what to write. | low | UX_copy |
| 8. Submit action alignment score | WeeklyReview Step 5: sliders + evidence fields | 3 sliders, 3 evidence text fields, verdict selector | Submit score | Verdict labels are opaque (aligned_progress, noisy_progress, etc.) with no explanation. Sliders lack context. | low | UX_copy |
| 9. View calibration/history | CalibrationHistory page | 3 lists: weekly reviews, action alignment scores, calibration scores | Read lists | Lists show raw IDs and scores. No detail view. No trend visualization. No "what does this mean?" explanation. | medium | frontend_gap |
| 10. Understand progress | P6Progress panel (in WeeklyReview) | P6 state flags (CODE_COMPLETE, NOT_VALIDATED, NOT_SEALED) | Read state | Flags are developer-facing labels, not user-friendly progress indicators. No "how many weeks done" counter. | medium | UX_copy |
| 11. Backup/export | CLI: alters-lab backup | tar.gz file created | Backup data | No frontend visibility. No "last backup" indicator. | low | defer |
| 12. Stop/uninstall | CLI: alters-lab stop / dpkg -r | Server stops / package removed | Stop/uninstall | Works cleanly | none | keep |

## Page-Level UX Audit

### GettingStarted
- **Purpose**: Onboarding checklist for new users
- **Current user value**: Low — static text, no interactivity
- **Data visibility**: None (static content)
- **Action clarity**: Clear — just reads instructions
- **Empty-state behavior**: N/A (always has content)
- **Error-state behavior**: N/A
- **Next-step clarity**: Low — no link to WeeklyReview or provider setup
- **Normal-use readiness**: Adequate (static info works)
- **P6-readiness relevance**: Low
- **UX gaps**: No progress tracking, no links to actual workflows, no "what's next" guidance

### SystemStatus
- **Purpose**: App health, route inventory, product status
- **Current user value**: Medium — shows runtime mode, provider mode, P6 state
- **Data visibility**: Good — shows config paths, provider mode, P6 flags
- **Action clarity**: One action: "Start Weekly Review" button
- **Empty-state behavior**: N/A (always has data)
- **Error-state behavior**: Shows error message
- **Next-step clarity**: Good — "Start Weekly Review" button is prominent
- **Normal-use readiness**: Good
- **P6-readiness relevance**: Low
- **UX gaps**: "Safe Endpoints" list is developer-facing. P6 state labels are developer-facing.

### ProviderSettings
- **Purpose**: Configure provider mode, manage secrets, test connectivity
- **Current user value**: High — full CRUD for provider config
- **Data visibility**: Good — shows current config, status, test results
- **Action clarity**: Good — clear save/test/delete actions
- **Empty-state behavior**: Shows "no config" state
- **Error-state behavior**: Shows error messages
- **Next-step clarity**: Good — test button after config
- **Normal-use readiness**: Good
- **P6-readiness relevance**: Low
- **UX gaps**: None significant

### WeeklyReview
- **Purpose**: 6-step weekly review flow
- **Current user value**: High — core workflow works end-to-end
- **Data visibility**: Good within steps — shows extracted fields, session state, scores
- **Action clarity**: Good — step buttons, clear actions per step
- **Empty-state behavior**: Step 1 shows template. Steps 2-6 disabled without note record.
- **Error-state behavior**: Shows error messages
- **Next-step clarity**: Step buttons guide progression
- **Normal-use readiness**: Good — core loop works
- **P6-readiness relevance**: High — this is where weekly evidence is created
- **UX gaps**: Step 3 hardcoded alters (should load from API). Step 5 verdict labels need explanation. No "previous reviews" sidebar.

### P6Progress (panel)
- **Purpose**: Show P6 validation state
- **Current user value**: Low — developer-facing flags
- **Data visibility**: Shows 3 boolean flags
- **Action clarity**: None (read-only)
- **Empty-state behavior**: N/A
- **Error-state behavior**: N/A
- **Next-step clarity**: None — flags don't tell user what to do next
- **Normal-use readiness**: Adequate (informational)
- **P6-readiness relevance**: Medium — shows validation state
- **UX gaps**: Labels are developer-facing. No progress counter. No "what to do next" guidance.

### CalibrationHistory
- **Purpose**: View calibration history, weekly reviews, action alignment scores
- **Current user value**: Medium — shows lists of records
- **Data visibility**: Lists raw IDs and scores. No detail view. No trend.
- **Action clarity**: None (read-only)
- **Empty-state behavior**: "No records yet" messages
- **Error-state behavior**: Shows error message
- **Next-step clarity**: None — no guidance on what to do with this data
- **Normal-use readiness**: Adequate (list view works)
- **P6-readiness relevance**: Medium — shows calibration evidence
- **UX gaps**: No detail drill-down. No trend visualization. No "what does this score mean?" explanation. No connection to RealityScore.

### RealityScore
- **Purpose**: Submit manual reality scores for calibration
- **Current user value**: Low — manual score submission, rarely used directly
- **Data visibility**: None (submit-only form)
- **Action clarity**: Good — sliders + submit button
- **Empty-state behavior**: N/A (form always present)
- **Error-state behavior**: Shows error message
- **Next-step clarity**: Low — "Go to Weekly Review" button exists but no guidance on when to use this page
- **Normal-use readiness**: Adequate (form works)
- **P6-readiness relevance**: Medium — calibration input
- **UX gaps**: No history of submitted scores. No connection to CalibrationHistory. Unclear when user should use this vs weekly review.

### AlterDialogue
- **Purpose**: Chat with alter personas
- **Current user value**: Low — no persistent history, no real provider dialogue
- **Data visibility**: Shows single reply only
- **Action clarity**: Good — type message, click send
- **Empty-state behavior**: Empty chat area
- **Error-state behavior**: Shows error message
- **Next-step clarity**: None
- **Normal-use readiness**: Low — replies not persisted, no conversation history
- **P6-readiness relevance**: Low
- **UX gaps**: No conversation history. No persistence. Single-turn only.

### RubricDelta
- **Purpose**: View rubric delta suggestions
- **Current user value**: Low — cold start, no real suggestions
- **Data visibility**: Shows suggestion JSON if any
- **Action clarity**: One button: "Generate Suggestion"
- **Empty-state behavior**: Empty area after click
- **Error-state behavior**: Shows error message
- **Next-step clarity**: None
- **Normal-use readiness**: Low — no data in cold start
- **P6-readiness relevance**: Low
- **UX gaps**: Cold start. No explanation of what rubric delta means.

### CheckpointPlan
- **Purpose**: View checkpoint regeneration plans
- **Current user value**: Low — cold start, no real plans
- **Data visibility**: Shows plan JSON if any
- **Action clarity**: One button: "Generate Plan"
- **Empty-state behavior**: Empty area after click
- **Error-state behavior**: Shows error message
- **Next-step clarity**: None
- **Normal-use readiness**: Low — no data in cold start
- **P6-readiness relevance**: Low
- **UX gaps**: Cold start. No explanation of what checkpoint plan means.

---

## Calibration/History UX Findings

| Question | Answer | Gap? |
|----------|--------|------|
| Can a user understand past action alignment scores? | Partially — list shows score_id and action_alignment_score, but no context on what the score means | Yes — no explanation of score meaning |
| Can a user inspect one score record? | No — no detail view, clicking is not possible | Yes — missing detail drill-down |
| Can a user see trend over time? | No — list is flat, no sorting by date, no trend visualization | Yes — missing trend view |
| Can a user understand whether behavior is improving? | No — no comparison between weeks, no trend indicator | Yes — missing progress indicator |
| Can a user distinguish weekly review, calibration record, and action alignment score? | Partially — three separate lists, but no explanation of relationship | Yes — missing relationship explanation |
| Can a user connect RealityScore to CalibrationHistory? | No — RealityScore is a separate page with no link to history | Yes — missing cross-page connection |
| What should be visible before implementation? | Weekly review list with dates, action alignment scores with verdict explanation, trend indicator, detail drill-down | — |

---

## UX Gap Table

| ux_gap_id | page_or_workflow | gap_type | severity | blocks_normal_use | blocks_p6_reconsideration | recommended_resolution_phase | notes |
|-----------|-----------------|----------|----------|-------------------|---------------------------|------------------------------|-------|
| UX-001 | CalibrationHistory | data_visibility | medium | false | false | P11-M5 | No detail drill-down for scores |
| UX-002 | CalibrationHistory | data_visibility | medium | false | false | P11-M5 | No trend visualization |
| UX-003 | CalibrationHistory | e2e_confusion | low | false | false | P11-M5 | No explanation of score meaning or relationship between record types |
| UX-004 | RealityScore | navigation | low | false | false | P11-M5 | No link to CalibrationHistory, no history of submitted scores |
| UX-005 | WeeklyReview | copy | low | false | false | P11-M5 | Step 3 hardcoded alters (should load from API) |
| UX-006 | WeeklyReview | copy | low | false | false | P11-M5 | Step 5 verdict labels need user-facing explanation |
| UX-007 | P6Progress | copy | medium | false | false | P11-M5 | Developer-facing labels, no progress counter, no "what next" |
| UX-008 | GettingStarted | navigation | low | false | false | defer | No links to actual workflows, no progress tracking |
| UX-009 | SystemStatus | copy | low | false | false | defer | "Safe Endpoints" and P6 state labels are developer-facing |
| UX-010 | AlterDialogue | data_visibility | low | false | false | defer | No conversation history, no persistence |
| UX-011 | RubricDelta | empty_state | low | false | false | defer | Cold start, no explanation |
| UX-012 | CheckpointPlan | empty_state | low | false | false | defer | Cold start, no explanation |

---

## Recommended P11-M4 Focus

**What to plan:**
- CalibrationHistory detail view and trend visualization
- RealityScore history and cross-page connection
- P6Progress user-facing labels and progress counter
- WeeklyReview Step 3 dynamic alter loading
- WeeklyReview Step 5 verdict explanation

**What not to plan:**
- Phase 3-6 route frontends (internal pipeline, not user-facing)
- AlterDialogue persistence (not needed for normal weekly use)
- Logs viewer (CLI doctor sufficient)
- Provider live setup (user-initiated)

**Implementation batch 1 (P11-M5):**
- CalibrationHistory detail/trend
- RealityScore history + CalibrationHistory connection
- P6Progress user-facing rewrite

**Implementation batch 2 (P11-M6):**
- Pattern review frontend
- Behavior validation frontend
- Data management visibility

**Deferred:**
- AlterDialogue persistence
- RubricDelta / CheckpointPlan cold-start improvements
- GettingStarted interactivity
- SystemStatus developer label cleanup
