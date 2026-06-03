# Route B v2 Approval Report

Date: 2026-06-03
Status: **COMPLETE — All 5 domains have data-backed Route B approved artifacts**

## Summary

Route B approval hardened from "literature metadata + rule aggregation" to "data-backed public baseline priors." Literature-only artifacts downgraded to contextual_prior (lab_only). Data-backed baselines from NLSY97 and MIDUS promoted to route_b_approved.

## Artifact Changes

### Downgraded (literature-only → contextual_prior)

| artifact_id | domain | old approved | new approved | reason |
|---|---|---|---|---|
| pa_lit_career_education | career_education | true | **false** | Literature-only, no actual data |
| pa_lit_financial | financial | true | **false** | Literature-only, no actual data |
| pa_lit_health | health | true | **false** | Literature-only, no actual data |
| pa_lit_relationship | relationship | true | **false** | Literature-only, no actual data |
| pa_lit_subjective_wellbeing | subjective_wellbeing | true | **false** | Literature-only, no actual data |

### Newly Data-Backed (NLSY97)

| artifact_id | domain | data source | n_valid | missingness |
|---|---|---|---|---|
| pa_nlsy97_career_education | career_education | NLSY97 2005 | 7,271-7,317 | 19% |
| pa_nlsy97_financial | financial | NLSY97 2005 | 6,110 | 32% |

### Retained (MIDUS data-backed)

| artifact_id | domain | data source | approved |
|---|---|---|---|
| pa_midus_chronic_conditions | health | MIDUS 1-3 | true |
| pa_midus_self_rated_health | health | MIDUS 1-3 | true |
| pa_midus_social_support | relationship | MIDUS 2 | true |
| pa_midus_life_satisfaction | subjective_wellbeing | MIDUS 1-3 | true |
| pa_midus_perceived_control | subjective_wellbeing | MIDUS 1-3 | true |

## 5-Domain Approval Matrix

| Domain | Data-Backed Artifacts | Model Card | approval_level | Status |
|---|---|---|---|---|
| career_education | pa_nlsy97_career_education | mc_nlsy97_career_education | route_b_approved | ✅ |
| financial | pa_nlsy97_financial | mc_nlsy97_financial | route_b_approved | ✅ |
| health | pa_midus_chronic_conditions, pa_midus_self_rated_health | mc_midus_chronic_conditions, mc_midus_self_rated_health | route_b_approved | ✅ |
| relationship | pa_midus_social_support | mc_midus_social_support | route_b_approved | ✅ |
| subjective_wellbeing | pa_midus_life_satisfaction, pa_midus_perceived_control | mc_midus_life_satisfaction, mc_midus_perceived_control | route_b_approved | ✅ |

## Contextual Priors (Visible but Not Route B Approved)

| artifact_id | domain | artifact_class | approval_level |
|---|---|---|---|
| pa_lit_career_education | career_education | contextual_prior | lab_only |
| pa_lit_financial | financial | contextual_prior | lab_only |
| pa_lit_health | health | contextual_prior | lab_only |
| pa_lit_relationship | relationship | contextual_prior | lab_only |
| pa_lit_subjective_wellbeing | subjective_wellbeing | contextual_prior | lab_only |

## Forecast Integration Behavior

- `list_approved_artifacts()` now filters by `approval_level == "route_b_approved"` AND `artifact_class in ("data_backed_baseline", "calibrated_model")`
- Contextual priors are loaded separately via `list_contextual_priors()`
- Domain predictions carry `artifact_class` field
- Route B summary includes `artifact_class` and `contextual_prior_ids`
- Frontend distinguishes "Data-backed Route B prior" from "Contextual literature prior only"

## Schema Changes

### PopulationPriorArtifact (new fields)
- `artifact_class`: contextual_prior | data_backed_baseline | calibrated_model
- `actual_data_used`: bool
- `baseline_table_id`: str | None
- `value_labels_confirmed`: bool
- `missingness_reviewed`: bool
- `validation_report_id`: str | None

### PopulationBaselineModelCard (new fields)
- `artifact_class`: contextual_prior | data_backed_baseline | calibrated_model
- `approval_level`: unapproved | lab_only | route_b_approved
- `approval_reason`: str
- `approval_blockers`: list[str]

### Guardrails
- contextual_prior cannot be route_b_approved
- data_backed_baseline must have actual_data_used=true
- route_b_approved requires empty approval_blockers
- approval_level syncs with approved_for_route_b flag

## NLSY97 Baseline Tables Created

Script: `labs/population_baseline/scripts/build_nlsy97_route_b_baselines.py`
Artifact: `labs/population_baseline/artifacts/nlsy97_route_b_baselines_v2.json`
Config: `labs/population_baseline/config/nlsy97_route_b_baselines_v2.yaml`
Docs: `labs/population_baseline/NLSY97_ROUTE_B_BASELINES_V2.md`

## MIDUS Baseline Tables Verified

Config: `labs/population_baseline/config/midus_route_b_baselines_v2.yaml`
Docs: `labs/population_baseline/MIDUS_ROUTE_B_BASELINES_V2.md`

## Tests

- 21 new guardrail tests added (test_route_b_approval_v2.py)
- 1830 total backend tests passing
- 0 failures

## Raw Data Safety

- No raw data committed to repository
- No individual-level data in outputs
- No personal probabilities emitted
- No life_score created
- NLSY97 data processed via streaming (50K sample from 8.1GB CSV)
- MIDUS data confirmed via pyreadstat metadata inspection
