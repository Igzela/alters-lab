p10_m6_week1_validation_evidence:
  date: 2026-05-28
  validation_start_date: 2026-05-28
  validation_week: 1
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
    score_value: 0.88
    verdict: aligned_progress
    record_reference: redacted_for_pii

  pattern_review:
    attempted: false
    created_after_validation_start: null
    status: not_attempted
    record_reference: null
    counts_for_final_pattern_review: false

  behavior_validation:
    run: false
    result: null
    p6_validated: false
    p6_sealed: false

  completion_counter_after_week1:
    real_weekly_reviews_after_start: 1
    calibration_or_action_alignment_records_after_start: 1
    pattern_reviews_after_start: 0
    days_elapsed_since_start: 0
    p6_ready_for_closeout: false

  boundaries:
    personal_content_committed: false
    runtime_records_committed: false
    provider_output_committed: false
    synthetic_evidence_counted: false
    prior_pilot_evidence_counted: false
    p6_validated: false
    p6_sealed: false

  notes: "Week 1 validation operations completed successfully. All API calls executed on packaged app running at 127.0.0.1:18790. Evidence generated from real validation use, not synthetic. Redacted references to protect PII."
