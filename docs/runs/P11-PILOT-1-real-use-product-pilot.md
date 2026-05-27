# P11-PILOT-1: Real-Use Product Pilot

**Date:** 2026-05-27
**Tester:** Claude Code (executor)
**App version:** P11 sealed (commit cb5b457)
**Mode:** packaged, provider_mode=mock

## Purpose

Exercise all visible product workflows end-to-end. Record friction, unclear UX, and blockers. The goal is not to prove correctness — it is to find whether a real user can understand and move through the product without hidden blockers.

## Workflow Observations

### 1. Status Page
- **State:** 12 nav buttons visible, all clickable
- **Observation:** P6 status correctly shows NOT_VALIDATED / NOT_SEALED. System health section visible. No navigation errors.
- **Friction:** None

### 2. Getting Started
- **State:** 4-step onboarding guide with actionable buttons
- **Observation:** "Open Provider Settings" and "Start Weekly Review" buttons navigate correctly. Boundaries section clearly states P6/P7/P8 seal status and provider output disclaimer.
- **Friction:** None — clear entry point for new user.

### 3. Weekly Review
- **State:** P6Progress panel + 6-step wizard
- **Observation:** "Your Progress" section shows review count. Validation status: "Not started". Next-step guidance: "Continue weekly reviews as pilot evidence; P6 validation start remains blocked until product completeness closeout." Wizard is clean and linear.
- **Friction:** None

### 4. Dialogue
- **State:** Alter selector + text input + Send button + mock reply
- **Observation:** Warning banner: "Replies are not persisted unless explicitly saved. Provider output is not fact." Mock provider returns "[Mock] Acknowledging: test message for pilot". Works as expected.
- **Friction:** None — mock mode works correctly.

### 5. Reality Score
- **State:** 4 sliders + alter dropdown + notes + submit
- **Observation:** Scores from weekly reviews shown in "Recent Action Alignment Scores" (5 entries). "Go to Weekly Review" and "View Calibration History" navigation links work. Manual score submission form is clear.
- **Friction:** None

### 6. History
- **State:** 59 weekly reviews listed
- **Observation:** Reviews sorted by date, explanation section visible. Each entry shows date and score. Navigation from Reality Score "View Calibration History" link works.
- **Friction:** None

### 7. Patterns
- **State:** Boundary banner + build button + list
- **Observation:** Orange boundary banner: "Pattern review is supporting evidence only. It does not validate or seal P6." "Build New Pattern Review" button works (created pattern_review_20260527T232609Z). Status correctly shows "insufficient_data" (expected with mock provider).
- **Friction:** None

### 8. Validation
- **State:** P6 not-started banner + run button + empty state
- **Observation:** Banner: "P6 validation status: Not started." "Run Evaluation" button present. Empty state: "No validation report yet." Correctly does not claim P6 is validated.
- **Friction:** None

### 9. Data
- **State:** Record counts + export buttons + archive disabled + delete panel
- **Observation:** 9 runtime areas with record counts. Export buttons present. Archive disabled with clear notice: "Archive requires exact record selection; disabled until record list/detail exists." Delete by Record ID panel has area + record_id + confirmation fields.
- **Friction:** None

### 10. Provider
- **State:** Mode selector + status + safety info
- **Observation:** Provider mode: disabled. Mode selector present. Safety info box visible.
- **Friction:** None

## Friction Summary

| Page | Friction | Severity |
|------|----------|----------|
| Status | None | — |
| Getting Started | None | — |
| Weekly Review | None | — |
| Dialogue | None | — |
| Reality Score | None | — |
| History | None | — |
| Patterns | None | — |
| Validation | None | — |
| Data | None | — |
| Provider | None | — |

## Boundary Checks

- No `alters/current/` files modified
- No `rubric.yaml` modified
- No runtime records committed
- No personal weekly notes committed
- No provider secrets exposed
- No real provider calls made
- P6 status: NOT_VALIDATED / NOT_SEALED — no claims of validation
- Provider output disclaimers present on Dialogue and Getting Started pages

## Conclusion

All 10 product workflows (Status, Getting Started, Weekly Review, Dialogue, Reality Score, History, Patterns, Validation, Data, Provider) are accessible, functional, and correctly guarded with boundary disclaimers. No hidden blockers found. The product is usable as a local personal tool.

**Pilot result: PASS — no friction observed.**
