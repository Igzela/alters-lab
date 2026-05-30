> **Note**: This is a historical design document. Phase references (Phase 0, P4) reflect the system's state at time of writing. For current status, see CLAUDE.md.

# Calibration System Workflow

## A. Purpose

The Calibration System evaluates how well reality and confirmed Alters match over time. It uses a two-speed calibration model: lightweight two-week check-ins plus full checkpoint regeneration at longer intervals.

This is NOT probability forecasting. This is NOT Brier scoring. This measures the gap between predicted life-state and actual outcomes.

## B. Input Requirements

Before any scoring can occur, ALL of the following must exist and be human-confirmed:

- **Snapshot**: `alters/current/snapshot.yaml` with `intake_status.phase: "completed"`
- **Branches**: `alters/current/branches.yaml` with 3-4 confirmed branches
- **Alters**: `alters/current/alters/alter_*.yaml` with confirmed alters
- **Dialogue**: At least one completed dialogue session per alter
- **Value Alignment**: At least one completed alignment report per alter
- **Rubric**: `alters/calibration/rubric.yaml` with `status: active`

If any input is missing, scoring cannot proceed. No invented values are permitted.

## C. Two-Speed Update Model

### Lightweight Check-In (every 2 weeks)

- User reports actual values for each dimension (1-5 scale)
- Compare against predicted values from alter personality_drift
- Compute drift per dimension and overall drift
- Log score file (`score_*.yaml`)
- If drift < threshold: continue
- If drift >= threshold: flag for checkpoint review

### Checkpoint Regeneration (on trigger)

Triggered when:
- Drift exceeds threshold (0.6) for two consecutive check-ins
- New life constraints emerge
- User explicitly requests review

At checkpoint:
- Full rubric review (human only)
- Dimensions may be re-evaluated
- Rubric evolution requires explicit human confirmation (see Evolution Policy)
- New predictions recorded for next cycle

## D. Dimensions and Drift Formula

### Dimensions

| Dimension | Description | Scale |
|-----------|-------------|-------|
| execution_discipline | Follow-through and consistency | 1-5 |
| exploration_freedom | Room for exploration and learning | 1-5 |
| life_state_match | Match with life constraints | 1-5 |
| energy_level | Sustainability given capacity | 1-5 |

### Drift Formula

```
For each dimension d:
  drift_d = abs(predicted[d] - actual[d]) / 4

Overall drift = mean(drift_d for all d)
```

- Range: 0.0 (perfect match) to 1.0 (maximum divergence)
- Checkpoint threshold: 0.6

## E. Cold-Start Policy

During cold start (first 3 checkpoints):

- No full rubric scoring
- No drift computation against predictions
- Only record actual values as baseline
- No score files created until baseline is established
- `alters/calibration/state.json` tracks cold-start status

Cold-start ends when:
- 3 check-ins have been completed with actual values
- A baseline of actual values exists for comparison

## F. Rubric Evolution Policy

The rubric CANNOT modify itself. All changes require explicit human review and confirmation.

- `auto_modify: false` is permanent — never set to true
- Dimension changes require human decision and decision record
- Scale changes require human decision and decision record
- Drift formula changes require human decision and decision record
- New dimensions require human decision and decision record

Evolution is triggered by:
1. Drift exceeding threshold for two consecutive checkpoints
2. New life constraints emerging
3. User explicitly requesting rubric review

## G. Valid/Invalid Patterns

### Valid Patterns

- Score file created only after confirmed snapshot, branch, alter, and dialogue
- Actual values reported by user (not invented)
- Predicted values sourced from alter personality_drift
- Drift computed from real predicted/actual pairs
- Rubric changes documented in decision record with human approval

### Invalid Patterns

- Score file created without confirmed inputs
- Actual values invented by the system
- Drift computed without both predicted and actual values
- Rubric modified without human confirmation
- Score files created during cold-start phase
- Auto-modification of rubric dimensions or formula

## H. Hard Prohibitions

1. **No Brier scoring**: The calibration system does not use Brier scores or probability forecasting. It measures life-state alignment, not prediction accuracy.
2. **No auto-modify**: The rubric cannot modify itself. `auto_modify: false` is permanent.
3. **No diagnostic-to-policy**: Diagnostic observations (drift values) cannot automatically trigger policy changes. All policy changes require human confirmation.
4. **No invented values**: Actual values must come from user-reported outcomes. No fabricated data.
5. **No active scores in Phase 0**: No `score_*.yaml` files are created until cold-start ends and checkpoints exist.
6. **No drift without both sides**: Drift cannot be computed without both predicted and actual values.
7. **No rubric self-evolution**: Rubric evolution requires explicit human review and a decision record.

## I. P4 Calibration Loop MVP Contract

Phase 4 introduces a narrow backend-only calibration loop surface:

- Reality score records may be created only from explicit user submission.
- Reality score writes are limited to `alters/calibration/scores/score_*.yaml`.
- `alters/current/**` remains out of bounds for calibration loop writes.
- `alters/calibration/rubric.yaml` remains read-only and cannot be changed by the API.
- Drift calculation is response-only evidence; it does not trigger regeneration, archive, promotion, or rubric delta.
- Calibration history is read-only; derived drift evidence may be computed in memory but is not persisted by the history endpoint.
- No LLM provider, frontend, database, archive, regeneration, or promotion path is part of P4-M2/M3/M4.
