# P10-M6: Validation Counters

**Date:** 2026-05-28
**Validation start date:** 2026-05-28

## Required Total for P6 Closeout

| Requirement | Target | Notes |
|-------------|--------|-------|
| Real weekly reviews after 2026-05-28 | 4 | Must be real, not synthetic |
| Calibration/action-alignment records after 2026-05-28 | 4 | One per weekly review |
| Pattern reviews after 2026-05-28 | 1 | Must evaluate valid post-start evidence |
| Time window | 21 days / 4 ISO weeks | From validation start date |

## Current Counters (Before Week 1)

| Counter | Current | Notes |
|---------|---------|-------|
| weekly_reviews_after_start | 0 | Pre-start reviews do not count |
| calibration_or_action_alignment_records_after_start | 0 | Pre-start records do not count |
| pattern_reviews_after_start | 0 | Pre-start reviews do not count |
| days_elapsed_since_start | 0 | Calculated from 2026-05-28 |

## What Does NOT Count

- P10-M2 note (pre-start)
- P10-M3 review (pre-start)
- P11 smoke (pre-start)
- P11-PILOT-1 (pre-start)
- Synthetic smoke data
- Provider output
- Any record created before 2026-05-28

## After Week 1 Execution

After Charlie completes Week 1 packaged-app operations, counters update to:

| Counter | Expected After Week 1 |
|---------|----------------------|
| weekly_reviews_after_start | 1 |
| calibration_or_action_alignment_records_after_start | 1 |
| pattern_reviews_after_start | 0 or 1 (optional) |
| days_elapsed_since_start | 7 (approximately) |
| p6_ready_for_closeout | false (need 3 more weeks) |
