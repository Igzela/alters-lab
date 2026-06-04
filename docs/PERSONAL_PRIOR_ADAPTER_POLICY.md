# Personal Prior Adapter Policy

## Purpose

The Personal Prior Adapter combines Route A personal evidence, Route B public priors, behavior metric completeness, outcome target progress, external evidence, and calibration history into a per-domain forecast decision. It does not train models, emit exact probabilities, or create a life score.

## Evidence Hierarchy

| Priority | Source | When strongest |
|----------|--------|----------------|
| 1 | external_evidence | Recent, objective, domain-specific |
| 2 | route_a_behavior trend | Short-term trajectory, 2+ weeks of data |
| 3 | route_b strong_calibrated | Validated population model with transfer-risk awareness |
| 4 | route_b data_backed | Descriptive baseline, no individual calibration |
| 5 | outcome_target progress | Concrete goal tracking |
| 6 | calibration_history | Forecast track record for this domain |
| 7 | route_b contextual | Literature explanation only, never drives direction |

## Route B Strength Levels

| Level | Meaning | Forecast influence |
|-------|---------|-------------------|
| strong_calibrated | NLSY97/MIDUS calibrated model, route_b_approved | Can materially affect direction; cannot override strong contradictory personal evidence |
| data_backed | Descriptive baseline from real data, route_b_approved | Can support or weaken confidence; should not dominate direction |
| contextual | Literature prior or unapproved model | Explanation only; never production-driving |
| unavailable | No Route B data | Not used |

## Influence Policy

### strong_calibrated

- Can raise or lower confidence when aligned with Route A
- Can shift direction when Route A is insufficient or mixed
- Cannot override strong (high-confidence) contradictory personal evidence
- Transfer risk is always present — strong prior ≠ personal destiny

### data_backed

- Supports baseline context and weakens or strengthens existing signals
- Cannot create high confidence alone
- Cannot shift direction when Route A has clear signal
- Useful for "favorable context but weak execution" and vice versa

### contextual

- Displayed for transparency
- Never drives adjusted_forecast_direction
- Cannot raise confidence above low

## Conflict Cases

| Route A | Route B | Alignment | Interpretation |
|---------|---------|-----------|----------------|
| positive | positive | aligned | Reinforcing — confidence boost |
| positive | negative | conflicted | Personal momentum against unfavorable prior — explain transfer risk |
| negative | positive | conflicted | Favorable context but weak execution — lower confidence |
| negative | negative | aligned | High-risk deterioration — flag urgency |
| insufficient | strong | route_b_only | Prior-led but low personalization — mark provisional |
| strong | insufficient | route_a_only | Personal evidence only — no population context |
| any | unavailable | insufficient_data | Cannot use prior |

## Conflict Levels

| Level | Condition |
|-------|-----------|
| none | Both sources agree or one is unavailable |
| low | Minor directional disagreement (e.g., stable vs improving) |
| medium | Clear directional disagreement (improving vs declining) |
| high | Strong personal evidence directly contradicts strong_calibrated prior |

## Forecast Readiness

| Level | Condition |
|-------|-----------|
| insufficient | No Route A data AND no Route B data |
| provisional | Route A available but < 3 metrics OR only data_backed/contextual Route B |
| usable | Route A with 3+ metrics AND (strong_calibrated OR data_backed Route B aligned) |
| strong | Route A with 3+ metrics, aligned strong_calibrated Route B, external evidence present |

## Rules

1. External evidence can override weak Route B.
2. Strong Route A behavior can reduce pessimism from unfavorable Route B, but cannot erase transfer risk.
3. strong_calibrated Route B increases confidence when aligned with Route A.
4. data_backed Route B supports baseline context but cannot create high confidence alone.
5. contextual prior cannot drive adjusted_forecast_direction.
6. Missing or stale behavior data lowers forecast_readiness.
7. Unknown remains unknown — never guessed.
8. No exact probabilities emitted.
9. No life_score created.
10. Route B never silently overrides Route A.
