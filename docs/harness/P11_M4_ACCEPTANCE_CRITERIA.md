# P11-M4: Acceptance Criteria

## P11-M5 Acceptance Criteria

### Build & Test
- [ ] Frontend build passes (`cd apps/web && npm run build`)
- [ ] Backend tests pass (`PYTHONPATH=apps/api/src python3 -m pytest apps/api/tests/ -q`)

### CalibrationHistory
- [ ] Score list shows all action alignment scores sorted by date
- [ ] Clicking a score row opens a detail panel with: score value + scale explanation, verdict label + human-readable meaning, verdict sentence, evidence fields, linked weekly review excerpt, date/timestamp
- [ ] Trend indicator shows up/down/stable arrow comparing most recent to previous score
- [ ] First score shows "first score" indicator (no trend)
- [ ] Page header explains: what action alignment score means, what verdict labels mean, relationship between weekly reviews and calibration records

### RealityScore
- [ ] Page shows recent calibration history (last 5 scores)
- [ ] Link to full CalibrationHistory page is present and functional
- [ ] Explanation text connects reality scores to calibration history

### P6Progress
- [ ] Labels are user-facing: "Weekly reviews completed: N", "Alignment scores recorded: N"
- [ ] Validation status shows "Not started (requires 4 weekly reviews over 21+ days)"
- [ ] Next-step guidance visible: "Complete weekly reviews to build validation evidence"
- [ ] P6 false flags remain correct (NOT_VALIDATED, NOT_SEALED)

### WeeklyReview Step 5
- [ ] Verdict selector shows human-readable descriptions for each option
- [ ] Descriptions are accurate: Aligned Progress, Noisy Progress, Drift, Stall

### WeeklyReview Step 3 (Optional)
- [ ] Alter dropdown loads from API (GET /alter-dialogue/alters)
- [ ] Alter list matches backend-reported alters

### Boundaries
- [ ] No P6 validation claim
- [ ] No provider calls
- [ ] No raw runtime records committed
- [ ] No active YAML/rubric changes
- [ ] No new backend routes
- [ ] No secrets committed

---

## P11-M6 Acceptance Criteria

### Build & Test
- [ ] Frontend build passes (`cd apps/web && npm run build`)
- [ ] Backend tests pass (`PYTHONPATH=apps/api/src python3 -m pytest apps/api/tests/ -q`)

### Pattern Review Page
- [ ] List view shows past pattern reviews with dates
- [ ] Detail view shows full pattern report
- [ ] Build button triggers pattern detection and shows result
- [ ] Page does NOT claim validation is complete
- [ ] Navigation entry added to App.tsx

### Behavior Validation Page
- [ ] Report view shows validation status (not started / in progress / complete)
- [ ] Evaluate button triggers validation check and shows result
- [ ] UI shows "validation not started" when no evidence exists
- [ ] UI does NOT claim P6 is validated
- [ ] P6 false flags remain correct
- [ ] Provider output is not counted as evidence
- [ ] Navigation entry added to App.tsx

### Data Management Page
- [ ] Manifest shows record counts by type (weekly notes, reviews, scores, etc.)
- [ ] Export button creates export and shows download link or confirmation
- [ ] Delete button shows confirmation dialog before deleting
- [ ] Archive button creates archive and shows confirmation
- [ ] No accidental data loss (all destructive actions require confirmation)
- [ ] Navigation entry added to App.tsx

### Boundaries
- [ ] P6 remains NOT_VALIDATED unless separately approved
- [ ] P6 remains NOT_SEALED
- [ ] No provider output persistence by default
- [ ] No active YAML/rubric mutation
- [ ] No real provider calls
- [ ] No secrets committed
- [ ] No raw personal records committed
- [ ] No new backend routes
