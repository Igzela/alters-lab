# P6 Closeout Operator Guide

P6 closeout is a verification operation, not an implementation milestone. It may pass only after behavior validation passes with verified persisted evidence.

## Operator Commands

Check current evidence without writing records:

```bash
python tools/p6_validation_check.py
```

Dry-run closeout attempt without saving validation:

```bash
python tools/p6_closeout_attempt.py --dry-run
```

After four real weekly review cycles, inspect the checklist and run a guarded validation attempt:

```bash
python tools/p6_closeout_attempt.py \
  --usage-integrity-pass \
  --behavior-improved \
  --save-validation
```

The flags above are operator attestations after reviewing real evidence. They are not substitutes for persisted weekly reviews, calibration records, pattern review, or the 4-week window. The runtime behavior validation service still verifies those records before it can return `P6_BEHAVIOR_VALIDATED`.

## Pass Conditions

Phase6 closeout can pass only if all are true:

- Latest behavior validation outcome is `P6_BEHAVIOR_VALIDATED`.
- The validation record has `evidence_verified=true`.
- Weekly review IDs, calibration record IDs, and pattern review IDs still load from `alters/product/**`.
- The verified weekly reviews cover a real 4-week window.
- No active YAML diff exists under `alters/current/**`.
- No rubric diff exists at `alters/calibration/rubric.yaml`.
- No raw P6 runtime records are tracked by git.

## Blocked Conditions

Closeout remains `BLOCKED` when:

- No behavior validation record exists.
- Behavior validation is `P6_INSUFFICIENT_DATA`.
- Behavior validation is `P6_USAGE_INVALID`.
- Behavior validation is `P6_FAILED_TO_VALIDATE`.
- A manual or fake validation record exists but cannot be re-verified against persisted evidence.
- Evidence exists but the time window is shorter than 21 days and does not cover 4 distinct ISO weeks.

## Sealing Rule

Do not mark P6 sealed in governance docs until `phase6_closeout/report` returns `PASS` against verified persisted evidence. P6 endgame automation can orchestrate the process, but it cannot seal P6 by itself.
