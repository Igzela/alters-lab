# Next Decision Point

## Current Status (v1.0 + LLM-Driven Calibration Complete — 2026-06-06)

V1.0 released (2026-06-04). LLM-Driven Calibration fully implemented — all 4 phases complete (behavior metrics, external evidence, frontend UI, outcome targets + predictor profile). See `docs/LDRIVEN_CALIBRATION_PLAN.md` for the full plan.

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

### Option A: Real User Pilot (Recommended)

LLM-Driven Calibration 全部完成。系统已具备完整的产品流 + LLM 引导对话，可以开始真实用户试用。

**为什么推荐：**
- 全部技术组件就绪，无阻塞项
- 真实用户反馈是验证系统价值的唯一方式
- P6 状态仍是 NOT_VALIDATED，pilot 数据可用于验证

### Option B: P6 Validation Gate

收集 pilot 数据后，推进 P6 的 validation sealing。

### Option C: Additional Model Cards

扩展 Route B coverage（relationship domain calibrated model 等）。低优先级——当前 5 域覆盖已足够。

## What Must NOT Happen

- No exact personal probabilities emitted
- No raw data committed to the repository
- No modification to active YAML or rubric
- No life_score field introduced
- No bypassing forecast snapshot / external evidence / evaluation / scorecard
