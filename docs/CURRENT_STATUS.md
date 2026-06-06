# Current Status

## v1.0 (Released 2026-06-04)

**Status**: v1.0 released, LLM-Driven Calibration all 4 phases complete

### System Health

| Metric | Value |
|--------|-------|
| Backend tests | 1980 passed, 2 skipped, 1 xpassed |
| Backend test files | 121 |
| Frontend tests | 84 passing |
| Frontend test files | 27 |
| Frontend build | Clean (3.2s) |
| OpenAPI typegen | 15,807 lines, 293 schemas |
| Life score | Confirmed absent (9+ guard-rail tests) |
| Exact probability | Confirmed banned (6+ guard-rail tests) |
| Provider safety audit | All sections PASS |

### Feature Status

| Feature | Status | Tests | Documentation |
|---------|--------|-------|---------------|
| Snapshot intake | Implemented | `test_snapshot_intake.py`, `test_snapshot_schema.py` | `docs/data-model.md` |
| Predictor profile | Implemented | `test_predictor_profile.py` | `docs/data-model.md` |
| Behavior metrics | Implemented | `test_behavior_metrics_catalog.py` | `docs/data-model.md` |
| Outcome targets | Implemented | `test_p6_endgame_tools.py` | `docs/data-model.md` |
| Branch forecast (Route A) | Implemented | `test_branch_forecast.py` | `docs/architecture.md` |
| Public priors (Route B) | Implemented | `test_route_b_v3_guardrails.py`, `test_public_priors.py` | `docs/architecture.md` |
| Personal prior adapter | Implemented | `test_personal_prior_adapter.py` | `docs/architecture.md` |
| Forecast snapshots | Implemented | `test_snapshot_intake.py` | `docs/data-model.md` |
| External evidence | Implemented | `test_phase3_closeout_api.py` | `docs/data-model.md` |
| Forecast evaluation | Implemented | `test_phase5_closeout.py` | `docs/data-model.md` |
| Calibration scorecard | Implemented | `test_phase5_closeout.py` | `docs/data-model.md` |
| Alter dialogue | Implemented | `test_alter_dialogue_api.py` | `docs/architecture.md` |
| Generation drafts | Implemented | `test_generation_drafts_api.py` | — |
| Draft review | Implemented | `test_draft_review.py` | — |
| Weekly review | Implemented | `test_cycle_summary_api.py` | — |
| LLM-driven calibration (Phase 1-4) | Implemented | `test_calibration_conversation.py` (Phase 1-2), frontend Phase 3-4 tests | `docs/LDRIVEN_CALIBRATION_PLAN.md` |
| Provider config | Implemented | `test_provider_config.py`, `test_provider_config_api.py` | — |
| Provider dialogue preview | Implemented | `test_provider_dialogue_preview.py` | — |
| Provider connectivity | Implemented | `test_provider_connectivity_api.py` | — |
| Population baseline (offline) | Experimental | `test_population_baseline_pilot.py`, phase15/16 tests | — |
| P6 runtime | Implemented | `test_p6_runtime_full.py`, `test_p6_endgame_tools.py` | — |
| Docker deployment | Implemented | Manual verified | — |
| CLI (start, stop, status, doctor, backup, load-sample) | Implemented | `test_local_launcher.py` | — |
| Data safety guardrails | Implemented | `test_data_safety.py` | — |
| YAML active loader | Implemented | `test_active_yaml_loader.py` | — |
| YAML validation CLI | Implemented | `test_validate_active_yaml_cli.py` | — |
| Route B strength matrix | Implemented | `test_route_b_v3_guardrails.py` | `docs/architecture.md` |
| SQLite repository backend | Experimental (code exists, YAML active) | — | — |
| Provider integration (LLM dialogue) | Experimental (optional, disabled by default) | — | — |

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

1. **Predictor Profile** -- captures traits, context, target domains
2. **Outcome Target** -- defines measurable goals per branch/domain
3. **Behavior Metrics** -- weekly structured indicators
4. **Branch Forecast** -- Route A + Route B + Adapter combined
5. **Forecast Snapshot** -- locked, immutable record of forecast
6. **External Evidence** -- real-world observations
7. **Forecast Evaluation** -- hit/miss/partial/unknown per domain, per source
8. **Calibration Scorecard** -- aggregate accuracy tracking

### What Is Production-Usable

- Core pipeline: snapshot -> branch discovery -> alter generation -> dialogue -> calibration
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

### LLM-Driven Calibration -- COMPLETE

**Plan: `docs/LDRIVEN_CALIBRATION_PLAN.md`**

LLM as conductor, guiding users through all calibration data extraction via natural conversation. Eliminates manual form-filling friction.

- **Phase 1** (behavior metrics + rubric scores): DONE -- schema, service, API router, frontend page, hooks, i18n, tests
- **Phase 2** (external evidence capture): DONE -- `ExternalEvidenceExtract` schema, service extraction + confirm logic
- **Phase 3** (extended frontend UI): DONE -- draft editing, conversation polish, error handling
- **Phase 4** (outcome targets + predictor profile): DONE -- extraction expanded to outcome targets and predictor profile

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

### Known Issues / Limitations

- P6 behavior validation gate: NOT_VALIDATED / NOT_SEALED -- requires real user data to seal
- Population baseline models are offline analysis scripts only, not runtime ML
- SQLite backend is implemented but YAML is the active storage format
- Provider (LLM) integration is optional and disabled by default; requires external API key
- No database -- all persistence is YAML + JSON files
- No multi-user support -- single-user local deployment only

### Next Steps

1. **Real user Pilot** -- onboard a real user to validate the product flow end-to-end
2. **P6 validation gate** -- collect enough real behavior data to seal P6
3. **Route B model coverage expansion** -- extend to more domains or improve `contextual` priors (low priority)
