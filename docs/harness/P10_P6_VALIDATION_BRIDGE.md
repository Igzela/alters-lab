# P10 P6 Validation Bridge

## Purpose

Define the exact conditions under which P6 validation can transition from `CODE_COMPLETE / NOT_VALIDATED / NOT_SEALED` to active validation.

## P6 Validation Start Conditions

All of the following must be true before P6 validation can begin:

1. **Explicit human decision** — Charlie explicitly says "start P6 validation"
2. **Explicit GPT confirmation** — GPT confirms the start decision
3. **Real weekly notes exist** — At least 4 real weekly note records from actual Obsidian usage
4. **Real weekly reviews exist** — At least 4 real weekly review sessions
5. **Calibration records exist** — At least 4 calibration records from real reviews
6. **Action alignment data exists** — At least 4 action alignment scores
7. **Time window satisfied** — At least 21 calendar days / 4 distinct ISO weeks
8. **No synthetic evidence** — None of the above records are synthetic/test data
9. **Clear start date** — P6 validation start date is explicitly recorded

## What P6 Validation Requires

| Requirement | Source | Minimum |
|-------------|--------|---------|
| Weekly note records | Real Obsidian ingest | 4 records |
| Weekly review records | Real review sessions | 4 records |
| Calibration records | Real calibration | 4 records |
| Action alignment scores | Real usage | 4 scores |
| Pattern review | Real usage | 1 review |
| Time window | Calendar | 21 days / 4 ISO weeks |
| Start decision | Human + GPT | Explicit |
| Start date | Recorded | One date |

## What P6 Validation Does NOT Accept

- Synthetic smoke records
- Provider-output-as-evidence
- Records created for testing
- Records from dev-mode runs
- Records without real weekly note backing
- Automatic or implicit validation start

## P6 State Transitions

```
CODE_COMPLETE / NOT_VALIDATED / NOT_SEALED
  ↓ (explicit human + GPT decision)
CODE_COMPLETE / VALIDATION_IN_PROGRESS / NOT_SEALED
  ↓ (all requirements met, 4 weeks complete)
CODE_COMPLETE / VALIDATED / SEALED
```

Each transition requires explicit authorization. No automatic transitions.
