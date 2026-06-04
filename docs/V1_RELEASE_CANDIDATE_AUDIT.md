# V1.0 Release Candidate Audit

**Date:** 2026-06-04
**Branch:** main
**Commit:** 8e65726 (Route B v4: Personal Prior Adapter + Strength-Aware Forecast Policy)

---

## 1. Backend Tests

| Metric | Value |
|--------|-------|
| Total | 1931 passed |
| Skipped | 2 |
| Xpassed | 1 |
| Failed | 0 |
| Duration | ~70s |

**Status:** ✅ PASS

---

## 2. Frontend Tests

| Metric | Value |
|--------|-------|
| Test Files | 25 passed |
| Tests | 81 passed |
| Failed | 0 |
| Duration | ~3.7s |

**Status:** ✅ PASS

---

## 3. Frontend Build

| Metric | Value |
|--------|-------|
| Build result | Clean |
| Duration | 3.22s |
| Output | dist/ with hashed assets |

**Status:** ✅ PASS

---

## 4. Repository / SQLite Status

- No `.db` or `.sqlite` files on disk
- Repository abstraction layer exists in code (`YamlRepository` + `SqliteRepository`)
- Active backend: **YAML files** under `alters/`
- SQLite is available as an opt-in alternative but not in use
- No data migration has occurred

**Status:** ✅ CLEAN — YAML-only, no orphaned databases

---

## 5. OpenAPI Typegen Status

- `apps/web/src/api-types.ts`: 15,807 lines
- Generated from FastAPI schema
- 293 TypeScript types/schemas

**Status:** ✅ CURRENT

---

## 6. Route B Strength Matrix

| Domain | Strength Level | Source |
|--------|---------------|--------|
| `career_education` | `strong_calibrated` | NLSY97 calibrated model |
| `financial` | `strong_calibrated` | NLSY97 calibrated model |
| `health` | `data_backed` | MIDUS data-backed baseline |
| `subjective_wellbeing` | `data_backed` | MIDUS data-backed baseline |
| `relationship` | `contextual` | Weak prior only |

**Strength level definitions:**
- `strong_calibrated`: artifact_class=calibrated_model + approval_level=route_b_approved
- `data_backed`: artifact_class=data_backed_baseline + approval_level=route_b_approved
- `contextual`: any artifact without route_b_approved
- `none`: no artifact available

**Priority:** strong_calibrated (3) > data_backed (2) > contextual (1) > none (0)

**Status:** ✅ All 5 domains covered, 2 strong + 2 data-backed + 1 contextual

---

## 7. Personal Prior Adapter Integration

| Component | Status |
|-----------|--------|
| Schema: `PersonalPriorAdapterSummary` | ✅ Defined |
| Schema: `PersonalPriorAdapterResult` | ✅ Defined |
| Schema: `EvidenceComponent` | ✅ Defined |
| Service: `adapt_personal_prior()` | ✅ Implemented |
| Integration: `analyze_branch_forecast()` calls adapter | ✅ Connected |
| Field: `BranchForecastResult.personal_prior_adapter` | ✅ Populated |
| Tests | ✅ 33 adapter tests passing |

**Key rules enforced:**
1. External evidence can override weak Route B
2. Strong Route A can reduce pessimism but cannot erase transfer risk
3. `strong_calibrated` Route B increases confidence when aligned
4. `data_backed` Route B supports baseline context only
5. `contextual` prior cannot drive adjusted direction
6. Missing/stale behavior data lowers forecast_readiness
7. Unknown remains unknown
8. No exact probabilities

**Status:** ✅ FULLY INTEGRATED

---

## 8. Forecast Snapshot Traceability

| Component | Status |
|-----------|--------|
| Schema: `ForecastSnapshotRecord` | ✅ Defined |
| Service: `save_snapshot()` | ✅ Implemented |
| Service: `load_snapshot()` | ✅ Implemented |
| Service: `list_snapshots()` | ✅ Implemented |
| Locked by default | ✅ `locked: bool = True` |
| Preserves full forecast payload | ✅ `forecast_payload` field |
| Preserves domain predictions | ✅ `domain_predictions` field |
| Preserves Route A summary | ✅ `route_a_summary` field |
| Preserves Route B summary | ✅ `route_b_summary` field |
| Preserves adapter summary | ✅ `adapter_summary` field |
| Preserves calibration divergence | ✅ `calibration_divergence_summary` field |
| Immutable after creation | ✅ No mutation endpoint |

**Status:** ✅ FULL TRACEABLE

---

## 9. Evaluation / Scorecard Traceability

### Forecast Evaluation

| Component | Status |
|-----------|--------|
| Schema: `ForecastEvaluationRecord` | ✅ Defined |
| Service: `evaluate_forecast()` | ✅ Implemented |
| Per-domain match results | ✅ `DomainResult.match_result` |
| Route A match tracking | ✅ `route_a_match_result` |
| Route B match tracking | ✅ `route_b_match_result` |
| Adapter match tracking | ✅ `adapter_match_result` |
| Match types | ✅ hit / miss / partial / unknown |
| Horizon tracking | ✅ provisional / final |
| Signal quality | ✅ predictive_signals / misleading_signals |

### Scorecard

| Component | Status |
|-----------|--------|
| Schema: `CalibrationScorecard` | ✅ Defined |
| Service: `build_scorecard()` | ✅ Implemented |
| Total evaluations | ✅ `total_evaluations` |
| Hit/miss/partial/unknown counts | ✅ Separate fields |
| Per-domain hit rates | ✅ `by_domain` list |
| Route A hit rates | ✅ `source_hit_rates.route_a_*` |
| Route B hit rates | ✅ `source_hit_rates.route_b_*` |
| Adapter hit rates | ✅ `source_hit_rates.adapter_*` |
| Conflict outcomes | ✅ `conflict_outcomes` dict |
| Calibration confidence | ✅ low / medium / high |
| Signal quality | ✅ `signal_quality` |

**Status:** ✅ FULL TRACEABILITY

---

## 10. Raw Data Safety

- No `.db` or `.sqlite` files committed
- `alters/current/` is gitignored (user data)
- `alters/sample/` contains only synthetic data
- No real user data in repository
- External evidence uses structured records, not raw data dumps
- Behavior metrics use weekly aggregates, not raw events

**Status:** ✅ SAFE

---

## 11. No life_score

- `life_score` field does not exist in any production schema
- All schemas use `extra="forbid"` — injecting it raises validation error
- 9+ test files explicitly assert its absence
- Guard-rail tests in: forecast_snapshot, branch_forecast, forecast_evaluation, scorecard, adapter, population_baseline, product_flow_e2e, prediction_calibration_flow, route_b_v3_guardrails

**Status:** ✅ CONFIRMED ABSENT

---

## 12. No Fake Exact Probability

- `exact_probability` not in `ALLOWED_OUTPUT_FIELDS` (public_prior_contract.py)
- `no_exact_probability_without_calibration` in `REQUIRED_GUARDS`
- `exact_probability_without_model_card` in `DISALLOWED_BEHAVIORS`
- 6+ test files assert exact probabilities are forbidden
- UI locale: "No exact probability is displayed."
- Service docstrings: "No exact probabilities"

**Status:** ✅ CONFIRMED BANNED

---

## Summary

| Audit Item | Status |
|------------|--------|
| Backend tests (1931) | ✅ PASS |
| Frontend tests (81) | ✅ PASS |
| Frontend build | ✅ PASS |
| Provider safety audit | ✅ ALL SECTIONS PASS |
| Repository/SQLite | ✅ CLEAN |
| OpenAPI typegen | ✅ CURRENT |
| Route B strength matrix | ✅ 5/5 domains |
| Personal Prior Adapter | ✅ INTEGRATED |
| Forecast snapshot traceability | ✅ FULL |
| Evaluation/scorecard traceability | ✅ FULL |
| Raw data safety | ✅ SAFE |
| No life_score | ✅ CONFIRMED |
| No fake probability | ✅ CONFIRMED |

**Overall: v1.0-rc audit PASS — no blockers found.**

See `docs/V1_RELEASE_READINESS.md` for the full go/no-go assessment. Recommendation: **v1.0 tag**.
