# P11-M3: Calibration/History UX Analysis

## Current State

The CalibrationHistory page (`CalibrationHistory.tsx`) shows three lists:
1. **Weekly Reviews** — session_id, status, note record id, next correction
2. **Action Alignment** — score_id, action_alignment_score, verdict_label
3. **Scores** — id, alter_id, actual_scores (from calibration-loop/history)

All are read-only lists with no detail view, no trend visualization, and no explanation of what the data means.

## UX Requirements (pre-implementation)

### Must Have (before P6 validation)

1. **Score detail drill-down**: Click a score to see full record (evidence, verdict sentence, date, linked weekly review)
2. **Trend indicator**: Show whether action alignment scores are improving/declining over time
3. **Score meaning explanation**: What does action_alignment_score of 0.75 mean? What do verdict labels mean?
4. **Record type distinction**: Help user understand difference between weekly review, calibration record, and action alignment score

### Should Have (before normal use is comfortable)

5. **RealityScore connection**: Show how manual reality scores relate to calibration history
6. **Weekly review summary**: Show review note excerpt, not just session_id
7. **Date-based ordering**: Sort records by date, not by ID

### Nice to Have (defer)

8. **Drift visualization**: Show drift calculations over time
9. **Comparison view**: Compare this week to last week
10. **Export capability**: Export calibration history as readable report

## What Should Be Visible Before Implementation

| Data Point | Currently Visible | Should Be Visible | Priority |
|------------|-------------------|-------------------|----------|
| Action alignment score value | Yes (raw number) | Yes + explanation of scale | high |
| Verdict label | Yes (raw label) | Yes + human-readable meaning | high |
| Verdict sentence | No | Yes (user's own words) | high |
| Evidence fields | No | Yes (one_action_evidence, etc.) | high |
| Linked weekly review | Partial (note record id) | Yes (review note excerpt) | medium |
| Date/timestamp | No | Yes (when score was submitted) | medium |
| Trend over time | No | Yes (sparkline or arrow indicator) | medium |
| Drift evidence | Partial (raw JSON) | Yes (human-readable summary) | low |
| Reality score history | No (separate page) | Yes (cross-reference) | low |

## Key Insight

The core issue is not that data is missing — it's that the **same data** is shown in raw form without context. A user who has completed 3 weekly reviews can see 3 score entries but cannot:
- Understand what 0.75 means (is that good?)
- See whether they're improving (was last week 0.65?)
- Connect the score to what they actually did (what was the evidence?)
- Know what to do next (what should I focus on this week?)

This is a **data visibility and explanation** gap, not a data creation gap. The backend already stores all the needed information. The frontend just needs to present it with context.
