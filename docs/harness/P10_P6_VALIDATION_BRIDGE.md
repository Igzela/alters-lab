# P10 P6 Validation Bridge

## Purpose

Define the exact conditions under which P6 validation can start and complete.

## P6 Validation Start Conditions

P6 validation can START after:

1. **Explicit human decision** — Charlie explicitly says "start P6 validation"
2. **Explicit GPT confirmation** — GPT confirms the start decision
3. **Clear start date** — P6 validation start date is explicitly recorded
4. **Real weekly notes exist** — At least 1 real weekly note from actual Obsidian usage

Start does NOT require 4 weeks of data. Start is a decision, not a completion.

## P6 Validation Completion / Seal Conditions

P6 validation can COMPLETE and seal only after all of the following:

| Requirement | Source | Minimum |
|-------------|--------|---------|
| Weekly note records | Real Obsidian ingest | 4 records |
| Weekly review records | Real review sessions | 4 records |
| Calibration records | Real calibration | 4 records |
| Action alignment scores | Real usage | 4 scores |
| Pattern review | Real usage | 1 review |
| Time window | Calendar | 21 days / 4 ISO weeks |
| No synthetic evidence | Verified | All records real |
| No provider-output-as-evidence | Verified | Clean source |
| Records backed by real weekly notes | Verified | Chain complete |
| Explicit GPT/human closeout decision | Human + GPT | Explicit |

## What P6 Validation Does NOT Accept

- Synthetic smoke records
- Provider-output-as-evidence
- Records created for testing
- Records from dev-mode runs
- Records without real weekly note backing
- Automatic or implicit validation start
- Validation completion without 4-week evidence window

## P6 State Transitions

```
CODE_COMPLETE / NOT_VALIDATED / NOT_SEALED
  ↓ (explicit human + GPT decision, start date recorded)
CODE_COMPLETE / VALIDATION_IN_PROGRESS / NOT_SEALED
  ↓ (all completion requirements met, 4 weeks complete, closeout decision)
CODE_COMPLETE / VALIDATED / SEALED
```

Each transition requires explicit authorization. No automatic transitions.
