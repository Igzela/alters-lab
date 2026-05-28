# P10-M6 Week 4 Validation Evidence Template

Fill this template after executing Week 4 packaged-app operations.

## Expected Counters After Week 4

| Counter | Expected |
|---------|----------|
| weekly_reviews_after_start | 4 |
| calibration_or_action_alignment_records_after_start | 4 |
| pattern_reviews_after_start | 1 |
| days_elapsed_since_start | >= 21 |
| p6_ready_for_closeout | may be true if all requirements met |

## Evidence

```yaml
p10_m6_week4_validation_evidence:
  date: <YYYY-MM-DD>
  validation_start_date: 2026-05-28
  validation_week: 4
  packaged_app_confirmed: true
  runtime_mode: packaged
  provider_mode: disabled_or_mock
  real_provider_call_made: false
  source_type: real_weekly_validation_use
  synthetic: false

  weekly_note:
    created_after_validation_start: true
    record_created: true
    record_reference: redacted_for_pii
    raw_note_committed: false

  weekly_review:
    created_after_validation_start: true
    completed: true
    record_created: true
    record_reference: redacted_for_pii
    raw_review_committed: false

  action_alignment:
    created_after_validation_start: true
    score_created: true
    score_value: <numeric>
    verdict: <label_only>
    record_reference: redacted_for_pii

  pattern_review:
    attempted: true
    created_after_validation_start: true
    status: <status>
    record_reference: redacted_for_pii
    counts_for_final_pattern_review: true

  completion_counter_after_week4:
    real_weekly_reviews_after_start: 4
    calibration_or_action_alignment_records_after_start: 4
    pattern_reviews_after_start: 1
    days_elapsed_since_start: <actual days, must be >= 21>
    p6_ready_for_closeout: <true only if all requirements met>

  boundaries:
    personal_content_committed: false
    runtime_records_committed: false
    provider_output_committed: false
    synthetic_evidence_counted: false
    prior_pilot_evidence_counted: false
    p6_validated: false
    p6_sealed: false

  notes: "<free text>"
```

## P6 Closeout Requirements

Before P6 can be closed out, ALL of the following must be true:

- weekly_reviews_after_start >= 4
- calibration_or_action_alignment_records_after_start >= 4
- pattern_reviews_after_start >= 1
- days_elapsed_since_start >= 21
- p6_ready_for_closeout: true
- No boundary violations
- GPT PASS verdict on Week 4 evidence

## Non-Countable Evidence

- P10-M2 does not count
- P10-M3 does not count
- P11 smoke does not count
- P11-PILOT-1 does not count
- provider output does not count
- synthetic data does not count
