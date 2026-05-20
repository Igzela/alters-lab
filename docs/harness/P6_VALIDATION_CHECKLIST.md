# P6 Validation Checklist

P6 behavior validation can only run after real persisted evidence exists. Code completion, helper automation, or operator intent is not validation.

## Required Evidence

- [ ] 4 weekly review records exist
- [ ] 4 calibration records exist
- [ ] 1 pattern review exists
- [ ] records span at least 4 weeks / 21 days minimum
- [ ] action alignment trend inspected
- [ ] repeated negative patterns inspected
- [ ] primary correction completion inspected
- [ ] usage integrity audited
- [ ] behavior_validation/evaluate result recorded
- [ ] phase6_closeout/report result recorded

## Blocking Conditions

- Missing weekly note or weekly review record.
- Missing action alignment calibration record.
- Missing 4-week pattern review.
- Evidence window shorter than 21 days unless records cover 4 distinct ISO weeks.
- Usage integrity is invalid.
- Metrics do not demonstrate behavior improvement.
- Latest behavior validation is absent, failed, usage invalid, insufficient data, or not backed by verified persisted evidence.

## Current Expected State

Until Charlie completes four real weekly review cycles, P6 state is:

- `CODE_COMPLETE`
- `P6_BLOCKED_BY_REAL_USE_WINDOW`
- `NOT_SEALED`
