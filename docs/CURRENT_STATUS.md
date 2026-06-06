# Current Status

## V1.0 + LLM-Driven Calibration Phase 1-2 Complete (2026-06-06)

**Status**: v1.0 released, LLM-Driven Calibration Phase 1-2 backend+frontend complete

### System Health

| Metric | Value |
|--------|-------|
| Backend tests | 1970 passing, 2 skipped, 1 xpassed |
| Frontend tests | 84 passing |
| Frontend build | Clean (3.2s) |
| OpenAPI typegen | 15,807 lines, 293 schemas |
| Life score | Confirmed absent (9+ guard-rail tests) |
| Exact probability | Confirmed banned (6+ guard-rail tests) |
| Provider safety audit | ✅ All sections PASS |
| Release readiness | ✅ GO — see V1_RELEASE_READINESS.md |

### Route B Strength Matrix

| Domain | Strength Level | Source |
|--------|---------------|--------|
| `career_education` | `strong_calibrated` | NLSY97 calibrated model |
| `financial` | `strong_calibrated` | NLSY97 calibrated model |
| `health` | `data_backed` | MIDUS data-backed baseline |
| `subjective_wellbeing` | `data_backed` | MIDUS data-backed baseline |
| `relationship` | `contextual` | Weak prior only |

All 5 domains covered. 2 strong + 2 data-backed + 1 contextual.

### Personal Prior Adapter

Fully integrated into the branch forecast pipeline. Combines Route A (personal evidence), Route B (population priors), and external evidence into per-domain adjusted forecasts. Key properties:

- External evidence can override weak Route B
- Strong Route A can reduce pessimism but cannot erase transfer risk
- `strong_calibrated` Route B increases confidence when aligned
- `contextual` prior cannot drive adjusted direction
- Unknown remains unknown
- No exact probabilities

### Forecast Traceability

Complete end-to-end traceability:

1. **Predictor Profile** → captures traits, context, target domains
2. **Outcome Target** → defines measurable goals per branch/domain
3. **Behavior Metrics** → weekly structured indicators
4. **Branch Forecast** → Route A + Route B + Adapter combined
5. **Forecast Snapshot** → locked, immutable record of forecast
6. **External Evidence** → real-world observations
7. **Forecast Evaluation** → hit/miss/partial/unknown per domain, per source
8. **Calibration Scorecard** → aggregate accuracy tracking

### What Is Production-Usable

- Core pipeline: snapshot → branch discovery → alter generation → dialogue → calibration
- Weekly review with trend analysis and pattern detection
- Forecast snapshots with full traceability
- External evidence recording
- Forecast evaluation with Route A / Route B / Adapter match tracking
- Calibration scorecard with per-source hit rates
- Personal Prior Adapter for combining all evidence sources
- Docker deployment
- CLI (start, stop, status, doctor, backup, load-sample)

### What Remains Experimental

- Population Baseline Lab (offline analysis scripts, not runtime ML)
- SQLite repository backend (code exists, YAML is active)
- Provider integration (LLM dialogue is optional, disabled by default)
- P6 behavior validation (collecting evidence, not yet sealed)

### LLM-Driven Calibration Progress

**Plan: `docs/LDRIVEN_CALIBRATION_PLAN.md`**

目标：LLM 作为主导者，通过自然对话引导用户完成所有校准数据的提取。消除手动填表的使用障碍。

- **Phase 1** (behavior metrics + rubric scores): COMPLETE -- schema, service, API router, frontend page, hooks, i18n, tests
- **Phase 2** (external evidence capture): COMPLETE -- `ExternalEvidenceExtract` schema, service extraction + confirm logic
- **Phase 3** (extended frontend UI): NEXT -- draft editing, conversation polish
- **Phase 4** (outcome targets + predictor profile): PLANNED

### Pilot Results

A seeded realistic pilot (25 tests) verified the full product flow:

- 1 predictor profile (mid-career professional)
- 2 branches (career_education + health)
- 4 weeks of behavior metrics
- 2 outcome targets
- Branch forecasts with Route A / Route B / Adapter visible
- Locked snapshots preserving all adapter results
- 3 external evidence records
- 2 evaluations with per-source match results
- Scorecard with Route A / Route B / Adapter hit tracking
- No life_score anywhere
- No exact probability anywhere
