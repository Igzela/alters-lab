# Next Decision Point

## Current Status (v1.0-rc — 2026-06-04)

V1.0 release candidate is complete. All release gates pass. Provider safety audit clean. Ready for v1.0 tag.

See `docs/V1_RELEASE_READINESS.md` for the full go/no-go assessment.

## What v1.0-rc Built

Since Phase 16, the following has been completed:

- **Route B productization** — 9 model cards, 10 approved artifacts, all 5 domains covered
- **Route B approval hardening** — artifact_class, approval_level, data-backed gate, 21 guardrail tests
- **Route B v3** — Calibrated public baseline models, NLSY97 career/financial, MIDUS health/wellbeing
- **Route B v4** — Personal Prior Adapter, strength-aware forecast policy, 33 adapter tests
- **Forecast snapshots** — locked immutable records preserving adapter results
- **External evidence** — structured observation recording
- **Forecast evaluation** — Route A / Route B / Adapter match tracking
- **Calibration scorecard** — aggregate accuracy with per-source hit rates
- **Frontend** — Public Priors page, Branch Forecast page, Personal Prior Adapter card
- **OpenAPI typegen** — 15,807 lines, 293 TypeScript types
- **E2E product flow test** — 14 tests verifying no life_score, Route B traceability
- **V1.0-rc pilot** — 25 tests verifying full product flow end-to-end
- **Bug fix** — trajectory variable used before definition in branch_forecast.py

## What Exists Now

- **Backend**: 1931 tests passing
- **Frontend**: 81 tests passing, build clean
- **Route B**: All 5 domains covered (2 strong_calibrated, 2 data_backed, 1 contextual)
- **Personal Prior Adapter**: Fully integrated
- **Traceability**: Forecast → snapshot → evidence → evaluation → scorecard
- **Safety**: No life_score, no exact probability, extra="forbid" on all schemas

## Next Recommended Steps

### Option A: Real User Pilot (Recommended)

The system is ready for a real user pilot over several weeks:

1. A real user creates their predictor profile and outcome targets
2. They record behavior metrics weekly
3. Branch forecasts are generated and locked as snapshots
4. External evidence is recorded as real events occur
5. Forecasts are evaluated against evidence
6. Scorecard accumulates calibration data

**What this validates:**
- Does the forecast system produce useful, non-obvious insights?
- Does the adapter correctly combine Route A + Route B + evidence?
- Does the calibration feedback loop improve over time?
- Are the directional predictions (not exact probabilities) actually helpful?

**Duration:** 4-8 weeks minimum for meaningful calibration data

### Option B: Additional Model Cards

Expand Route B coverage with additional datasets:

- Relationship domain: currently contextual only
- Financial domain: additional calibrated models
- Cross-source harmonization: link NLSY97 and MIDUS variables

### Option C: Frontend Polish

- Mobile responsiveness improvements
- Accessibility audit
- PDF export for calibration reports
- Keyboard shortcuts for all workflows

## What Must NOT Happen

- No exact personal probabilities emitted
- No raw data committed to the repository
- No modification to active YAML or rubric
- No life_score field introduced
- No bypassing forecast snapshot / external evidence / evaluation / scorecard
