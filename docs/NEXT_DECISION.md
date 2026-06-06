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

### Option A: LLM-Driven Calibration (Recommended)

**Full plan: `docs/LDRIVEN_CALIBRATION_PLAN.md`**

核心想法：LLM 作为主导者，通过自然对话引导用户完成所有校准数据的提取。用户只需聊天，不需要手动填表。

**4 个 Phase：**
- **Phase 1** — Behavior metrics + rubric scores 的对话式提取（最小可用版本）
- **Phase 2** — External evidence 的对话式捕捉
- **Phase 3** — 前端对话界面 + draft 确认卡片
- **Phase 4** — 扩展到 outcome targets 和 predictor profile

**关键设计决策：**
- 自由聊天，LLM 自己判断提取什么（不是分步填表）
- Draft-then-confirm：LLM 提取的数据先存为 draft，用户确认后写入
- Prompt-based JSON extraction（`<extraction>JSON</extraction>` 标签），不依赖 tool_use
- 复用现有 provider_gateway，不引入新 provider 依赖
- `submitted_by_user` 限制不变——LLM 不能自动提交，必须用户确认

**为什么推荐：**
- 当前最大障碍是用户手动填表——LLM 引导可以消除这个障碍
- 现有 LLM 基础设施（provider_gateway、weekly_review_assistant 模式）可以复用
- 不修改现有 schema 或 service，是纯增量的新增

### Option B: Real User Pilot

系统已具备完整的产品流，可以开始真实用户试用。但手动填表的体验问题会阻碍数据积累。建议先做 Option A（LLM 引导），再做 pilot。

### Option C: Additional Model Cards

扩展 Route B coverage（relationship domain calibrated model 等）。低优先级——当前 5 域覆盖已足够。

## What Must NOT Happen

- No exact personal probabilities emitted
- No raw data committed to the repository
- No modification to active YAML or rubric
- No life_score field introduced
- No bypassing forecast snapshot / external evidence / evaluation / scorecard
