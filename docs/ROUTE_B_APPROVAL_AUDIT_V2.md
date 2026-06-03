# Route B Approval Audit v2

Date: 2026-06-03
Auditor: Claude Code
Trigger: Route B Approval Hardening v2 — replace literature-only approval with data-backed public priors

## Executive Summary

**Current state: All 9 model cards have `approved_for_route_b: true`.** This is over-approved. Literature-only artifacts lack numerical effect sizes, calibration metrics, or validated baseline data. They should not count as Route B approved.

**Key finding:** 4 literature-only model cards are approved without any actual data backing. NLSY97 career/financial domains have NO product-level artifacts at all — baseline tables exist only in the lab.

## Artifact Classification

### Classes

| Class | Definition | Route B Eligible |
|---|---|---|
| `contextual_prior` | Literature-only, directional, no numeric baseline | No (unless explicit numerical meta-analysis) |
| `data_backed_baseline` | Descriptive baseline from actual dataset | Yes |
| `calibrated_model` | Model with validation metrics (Brier, AUC, etc.) | Yes |
| `invalid_or_overapproved` | Currently approved but doesn't meet criteria | Must downgrade |

### Classification of Each Artifact

#### Literature-Only Artifacts (5)

| artifact_id | domain | model_id | prior_type | Classification | should_remain_approved | reason |
|---|---|---|---|---|---|---|
| `pa_lit_career_education` | career_education | mc_lit_career_financial | textual | `contextual_prior` | **No** | No actual data, no numeric effect sizes, no calibration |
| `pa_lit_financial` | financial | mc_lit_career_financial | textual | `contextual_prior` | **No** | No actual data, no numeric effect sizes, no calibration |
| `pa_lit_health` | health | mc_lit_health | textual | `contextual_prior` | **No** | No actual data, no numeric effect sizes, no calibration |
| `pa_lit_relationship` | relationship | mc_lit_relationship | textual | `contextual_prior` | **No** | No actual data, no numeric effect sizes, no calibration |
| `pa_lit_subjective_wellbeing` | subjective_wellbeing | mc_lit_subjective_wellbeing | textual | `contextual_prior` | **No** | No actual data, no numeric effect sizes, no calibration |

**All 5 literature artifacts currently approved via model card. All should be downgraded.**

Common deficiencies across all literature artifacts:
- `probability_band: null`
- `population_percentile: null`
- `deviation_from_baseline: null`
- All calibration metrics: null
- No baseline table referenced
- No validation report

#### MIDUS Baseline Table Artifacts (5)

| artifact_id | domain | model_id | prior_type | Classification | should_remain_approved | reason |
|---|---|---|---|---|---|---|
| `pa_midus_chronic_conditions` | health | mc_midus_chronic_conditions | baseline_table | `data_backed_baseline` | **Yes** | Actual MIDUS data, baseline table exists |
| `pa_midus_life_satisfaction` | subjective_wellbeing | mc_midus_life_satisfaction | baseline_table | `data_backed_baseline` | **Yes** | Actual MIDUS data, baseline table exists |
| `pa_midus_perceived_control` | subjective_wellbeing | mc_midus_perceived_control | baseline_table | `data_backed_baseline` | **Yes** | Actual MIDUS data, baseline table exists |
| `pa_midus_self_rated_health` | health | mc_midus_self_rated_health | baseline_table | `data_backed_baseline` | **Yes** | Actual MIDUS data, baseline table exists |
| `pa_midus_social_support` | relationship | mc_midus_social_support | baseline_table | `data_backed_baseline` | **Yes** | Actual MIDUS data, baseline table exists |

**MIDUS artifacts use actual SPSS data confirmed via pyreadstat.** Missingness audited. Cross-wave analysis completed. These qualify as data-backed baselines, but need strengthening:
- Value labels need verification in artifact YAML
- Missingness rates need to be included in artifact YAML
- Baseline table ID needs to be linked

#### NLSY97 Artifacts (0 in product, 12 in lab)

**No NLSY97 artifacts exist in `alters/product/population_prior_artifacts/`.** NLSY97 baseline tables exist only in `labs/population_baseline/artifacts/nlsy97_baseline_tables_p16.json` with `approved_for_route_b: false`.

The lab has 12 aggregate tables: demographics (4), education (3), employment (3), financial (2). These are Round 1 only, from a 50K-row sample, with no value labels mapped.

**Impact:** career_education and financial domains have NO data-backed Route B artifacts.

#### Model Cards (9)

| model_id | model_family | approved_for_route_b | Classification | should_remain_approved | reason |
|---|---|---|---|---|---|
| `mc_lit_career_financial` | literature_prior_only | true | `invalid_or_overapproved` | **No** | Literature-only, no data |
| `mc_lit_health` | literature_prior_only | true | `invalid_or_overapproved` | **No** | Literature-only, no data |
| `mc_lit_relationship` | literature_prior_only | true | `invalid_or_overapproved` | **No** | Literature-only, no data |
| `mc_lit_subjective_wellbeing` | literature_prior_only | true | `invalid_or_overapproved` | **No** | Literature-only, no data |
| `mc_midus_chronic_conditions` | baseline_table | true | `data_backed_baseline` | **Yes** | Actual MIDUS data |
| `mc_midus_life_satisfaction` | baseline_table | true | `data_backed_baseline` | **Yes** | Actual MIDUS data |
| `mc_midus_perceived_control` | baseline_table | true | `data_backed_baseline` | **Yes** | Actual MIDUS data |
| `mc_midus_self_rated_health` | baseline_table | true | `data_backed_baseline` | **Yes** | Actual MIDUS data |
| `mc_midus_social_support` | baseline_table | true | `data_backed_baseline` | **Yes** | Actual MIDUS data |

## Domain Coverage Matrix (Current → Target)

| Domain | Current Artifacts | Current Approved | Target: Data-Backed Approved | Gap |
|---|---|---|---|---|
| career_education | 1 lit-only | 1 (over-approved) | NLSY97 baseline | **Need NLSY97 artifact** |
| financial | 1 lit-only | 1 (over-approved) | NLSY97 baseline | **Need NLSY97 artifact** |
| health | 1 lit + 1 MIDUS | 2 (1 over-approved) | MIDUS baseline | Downgrade lit, keep MIDUS |
| relationship | 1 lit + 1 MIDUS | 2 (1 over-approved) | MIDUS baseline | Downgrade lit, keep MIDUS |
| subjective_wellbeing | 1 lit + 2 MIDUS | 3 (1 over-approved) | MIDUS baselines | Downgrade lit, keep MIDUS |

## Required Actions

1. **Downgrade 4 literature model cards** — set `approved_for_route_b: false`
2. **Keep 5 MIDUS model cards** — add new schema fields (artifact_class, actual_data_used, etc.)
3. **Build NLSY97 career/financial baseline artifacts** — from existing lab baseline tables
4. **Build NLSY97 career/financial model cards** — new data-backed model cards
5. **Add schema guardrails** — prevent literature-only approval
6. **Update forecast integration** — filter by artifact_class
7. **Update frontend** — show approval status per domain
