# P6 Endgame Real-Use Validation Runbook

## 1. Current State

- P6 runtime code complete is merged to `main`.
- Behavior validation has not started because real 4-week evidence is not complete.
- Phase6 closeout is blocked until behavior validation passes with verified persisted evidence.
- P6 is not behavior validated.
- P6 is not sealed.

## 2. Weekly Process

Run this once per real week. Do not combine multiple fake weeks into one day and do not edit timestamps to satisfy the validation window.

1. Charlie writes an Obsidian weekly note using [P6_WEEKLY_REVIEW_TEMPLATE.md](P6_WEEKLY_REVIEW_TEMPLATE.md).
2. Ingest the raw note via `/obsidian-weekly-note/ingest`, or with:

   ```bash
   python tools/p6_weekly_review_flow.py path/to/weekly-note.md \
     --review-note "..." \
     --primary-next-correction "..." \
     --direction-alignment 0.0 \
     --execution-consistency 0.0 \
     --avoidance-level 0.0 \
     --one-action-evidence "..." \
     --one-avoidance-or-friction-evidence "..." \
     --one-next-correction "..." \
     --verdict-label noisy_progress \
     --verdict-sentence "..."
   ```

3. Start review via `/weekly-review/start`.
4. Complete review via `/weekly-review/{session_id}/complete`.
5. Score action alignment via `/action-alignment/score`.
6. Optional: run self-deception challenge when the note or review shows softened negative evidence.
7. Optional: run alter recommendation for review framing.
8. Complete or skip weekly reminder. Skips must have a reason and count toward usage integrity.

The helper script prints generated IDs. Runtime records are written under ignored `alters/product/**` paths and must not be committed raw.

## 3. Week 1-4 Evidence Table

| Week | week_id | raw note present | weekly_note_record_id | weekly_review_session_id | calibration_record_id | reminder status | primary correction | completion status | notes |
|------|---------|------------------|-----------------------|--------------------------|-----------------------|-----------------|--------------------|-------------------|-------|
| Week 1 | TBD | no | TBD | TBD | TBD | TBD | TBD | pending Charlie raw note | Await real Week 1 Obsidian note. |
| Week 2 | TBD | no | TBD | TBD | TBD | TBD | TBD | blocked by time | Execute one real week after Week 1. |
| Week 3 | TBD | no | TBD | TBD | TBD | TBD | TBD | blocked by time | Execute one real week after Week 2. |
| Week 4 | TBD | no | TBD | TBD | TBD | TBD | TBD | blocked by time | Execute one real week after Week 3. |

Update this table from sanitized IDs only. Do not paste raw personal note content into committed docs.

## 4. Pattern Review

- Run pattern review only after 4 weekly reviews exist.
- Pattern review must use real week IDs from the four completed weekly review cycles.
- Pattern review must not be fabricated.
- Pattern review must not be created from placeholder weeks.
- A pattern review with fewer than 4 evaluated weeks cannot satisfy behavior validation.

## 5. Behavior Validation

Run behavior validation only after real Week 1-4 evidence exists. Required inputs:

- 4 weekly review IDs.
- 4 calibration record IDs.
- 1 pattern review ID.
- Usage integrity audit.
- Behavior metrics inspection.

The validation service must not pass with fake IDs and must not pass with a short evidence window. Request booleans alone are insufficient; persisted evidence is loaded and verified before `P6_BEHAVIOR_VALIDATED` can be returned.

Use:

```bash
python tools/p6_validation_check.py
python tools/p6_closeout_attempt.py --dry-run
```

After checklist review confirms the metrics and usage integrity:

```bash
python tools/p6_closeout_attempt.py --usage-integrity-pass --behavior-improved --save-validation
```

## 6. Closeout

Phase6 closeout may run only after behavior validation passes. It must remain `BLOCKED` otherwise.

Closeout pass requires:

- Latest validation outcome is `P6_BEHAVIOR_VALIDATED`.
- Latest validation was produced from verified persisted evidence.
- Evidence still exists on disk and re-verifies.
- No active YAML diff.
- No rubric diff.
- No tracked raw P6 runtime records.

Do not mark P6 sealed until closeout returns `PASS`.

## 7. Failure Branches

| Failure | Required Response |
|---------|-------------------|
| Missing weekly note | Stop the weekly flow. Ask Charlie for the raw Obsidian weekly note. |
| Skipped week | Record a skipped reminder with reason. Validation window continues only when real weekly review evidence exists. |
| Insufficient evidence | Keep P6 in `P6_VALIDATION_IN_PROGRESS` or `P6_BLOCKED_BY_REAL_USE_WINDOW`. |
| No behavior improvement | Return `P6_FAILED_TO_VALIDATE`; do not seal. Decide whether to redesign after usage integrity audit. |
| Usage integrity invalid | Return `P6_USAGE_INVALID`; fix usage behavior before adding features. |
| Behavior validation failed | Keep closeout blocked. Do not manually write validating records. |
| Closeout blocked | Keep P6 not sealed and preserve the blocker reason in governance docs. |

## 8. Current Next Action

Charlie must provide the Week 1 raw Obsidian weekly note. Until then no runtime records should be created for Week 1, and P6 remains `CODE_COMPLETE`, `P6_BLOCKED_BY_REAL_USE_WINDOW`, and `NOT_SEALED`.
