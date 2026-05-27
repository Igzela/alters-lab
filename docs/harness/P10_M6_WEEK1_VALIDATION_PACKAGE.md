# P10-M6: Week 1 Validation Package

**Date:** 2026-05-28
**Status:** ready_for_human_execution

## Current P6 State

- P6: CODE_COMPLETE / VALIDATION_IN_PROGRESS / NOT_SEALED
- validation_start_date: 2026-05-28
- P6 is NOT validated
- P6 is NOT sealed

## Week 1 Required Human Operation

Charlie must perform the following in the packaged app:

1. **Use packaged app only** — not dev server, not raw code
2. **Provider mode: disabled or mock only** — no real provider calls
3. **Ingest one real weekly note** created after validation start (2026-05-28)
4. **Complete one real weekly review** after validation start
5. **Create one action alignment/calibration score** after validation start
6. **Optionally run PatternReview** — if insufficient_data, record as supporting status only; do not count as final pattern review unless it evaluates valid post-start evidence

## Countable Local Records

| Record | Countable? |
|--------|-----------|
| weekly_note_record_created_after_start | yes/no |
| weekly_review_record_created_after_start | yes/no |
| action_alignment_score_created_after_start | yes/no |
| calibration_record_created_after_start | yes/no (if separate) |
| pattern_review_created_after_start | yes/no (optional for Week 1) |
| behavior_validation_report | optional, must not validate/seal P6 |

## Non-Countable Evidence

The following do NOT count toward P6 completion:

- P10-M2 note (pre-start)
- P10-M3 review (pre-start)
- P11 smoke (pre-start)
- P11-PILOT-1 (pre-start)
- Synthetic smoke data
- Provider output
- Docs-only evidence
- Screenshots without local record references

## Redacted Repo Evidence Policy

- Raw weekly note remains local
- Raw weekly review remains local
- Runtime records remain local
- Repo gets only redacted summary
- No API keys/secrets
- No provider prompts/responses
- No personal content

## Important Distinctions

- Week 1 is NOT completion — it is the first of 4 required weeks
- Starting validation does NOT validate P6
- Starting validation does NOT seal P6
- Prior pilot/smoke evidence does NOT count for completion
- P6 completion requires: 4 real weekly reviews, 4 calibration records, 1 pattern review, 21 days / 4 ISO weeks
