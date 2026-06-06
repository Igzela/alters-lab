# Next Decision Point

## Current Status (v1.0 + LLM-Driven Calibration Phase 1-2 — 2026-06-06)

V1.0 released (2026-06-04). LLM-Driven Calibration Phase 1 (behavior metrics + rubric scores) and Phase 2 (external evidence capture) are complete — backend schema/service/API and frontend page/hooks/i18n all implemented.

See `docs/LDRIVEN_CALIBRATION_PLAN.md` for the full plan.

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

- **Backend**: 1970 tests passing
- **Frontend**: 84 tests passing, build clean
- **Route B**: All 5 domains covered (2 strong_calibrated, 2 data_backed, 1 contextual)
- **Personal Prior Adapter**: Fully integrated
- **Traceability**: Forecast → snapshot → evidence → evaluation → scorecard
- **Safety**: No life_score, no exact probability, extra="forbid" on all schemas

## Next Recommended Steps

### Option A: LLM-Driven Calibration Phase 3-4 (Recommended)

**Full plan: `docs/LDRIVEN_CALIBRATION_PLAN.md`**

Phase 1 (behavior metrics + rubric scores extraction) and Phase 2 (external evidence capture) are **complete**. Backend schema/service/API and frontend page/hooks/i18n all implemented.

**Remaining:**
- **Phase 3** — Extended frontend UI: draft editing inline, conversation polish, error handling
- **Phase 4** — Expand extraction to outcome targets + predictor profile

**为什么推荐：**
- Phase 1-2 已完成，Phase 3-4 是自然延续
- Phase 4 对新用户价值最大（引导定义 outcome targets 和 predictor profile）

### Option B: Real User Pilot

系统已具备完整的产品流 + LLM 引导对话。可以开始真实用户试用。建议在 Phase 3 完成后启动 pilot。

### Option C: Additional Model Cards

扩展 Route B coverage（relationship domain calibrated model 等）。低优先级——当前 5 域覆盖已足够。

## What Must NOT Happen

- No exact personal probabilities emitted
- No raw data committed to the repository
- No modification to active YAML or rubric
- No life_score field introduced
- No bypassing forecast snapshot / external evidence / evaluation / scorecard
