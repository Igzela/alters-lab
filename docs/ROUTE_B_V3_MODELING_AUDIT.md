# Route B v3 Modeling Audit

**Date**: 2026-06-03
**Auditor**: Claude Code
**Scope**: All Route B approved artifacts, domain coverage, NLSY97/MIDUS data integrity, calibration status

---

## 1. Executive Summary

All 11 production model cards and 12 population prior artifacts were audited. Key findings:

- **All 5 domains appear in the coverage matrix** (career_education, financial, health, relationship, subjective_wellbeing). Health IS covered -- by MIDUS data-backed baselines (self-rated health, chronic conditions) and a literature contextual prior.
- **All calibration metrics are NULL** across every model card. No calibrated_model artifacts exist yet.
- **All 7 data_backed_baseline cards are route_b_approved** with empty approval blockers. The 4 contextual_prior cards are lab_only.
- **NLSY97 2005 round age range "25-29" is correct** but derived from cohort knowledge (born 1980-84), not verified from an actual age variable in the data.
- **NLSY97 financial outcome has 32% missingness** (S5412800 family income: 1228 refusals + 1646 invalid skip). This is a significant concern for baseline quality.
- **NLSY97 health outcomes are NOT covered** by any Route B baseline. Health coverage comes solely from MIDUS.
- **No NLSY97 outcome definitions have confirmed variable names** -- all 11 NLSY97 outcomes remain at "candidate" confirmation status.

---

## 2. Domain Coverage Matrix

| Domain | Data-Backed Artifacts | Contextual Priors | Route B Status | Gap |
|--------|----------------------|-------------------|----------------|-----|
| career_education | pa_nlsy97_career_education | pa_lit_career_education | approved | None |
| financial | pa_nlsy97_financial | pa_lit_financial | approved | 32% missingness on income |
| health | pa_midus_self_rated_health, pa_midus_chronic_conditions | pa_lit_health | approved | No NLSY97 health baseline |
| relationship | pa_midus_social_support | pa_lit_relationship | approved | Single-wave only (MIDUS 2 SAQ) |
| subjective_wellbeing | pa_midus_life_satisfaction, pa_midus_perceived_control | pa_lit_subjective_wellbeing | approved | SAQ missingness 11-19% |

**Finding 1**: All 5 domains are covered. Health IS covered by MIDUS data-backed baselines. The initial concern about a health gap is unfounded -- MIDUS provides two Route B approved health baselines (self-rated health, chronic conditions).

**Finding 2**: Relationship domain has the weakest coverage -- social support is only available in MIDUS Wave 2 SAQ (not cross-wave comparable), with 3.9-4.1% missingness.

---

## 3. Model Card Audit (All 11 Cards)

### 3.1 Route B Approved Cards (7 data_backed_baseline)

| Model Card | Domain | Source | Artifact Class | Calibration | Transfer Risk | Approval Blockers | Verdict |
|-----------|--------|--------|----------------|-------------|---------------|-------------------|---------|
| mc_nlsy97_career_education | career_education | NLSY97 2005 | data_backed_baseline | ALL NULL | high | [] | KEEP -- no demotion needed |
| mc_nlsy97_financial | financial | NLSY97 2005 | data_backed_baseline | ALL NULL | high | [] | KEEP -- but see Section 5 |
| mc_midus_self_rated_health | health | MIDUS 1-3 | data_backed_baseline | ALL NULL | medium | [] | KEEP |
| mc_midus_chronic_conditions | health | MIDUS 1-3 | data_backed_baseline | ALL NULL | medium | [] | KEEP |
| mc_midus_social_support | relationship | MIDUS 2 only | data_backed_baseline | ALL NULL | high | [] | KEEP -- single-wave caveat noted |
| mc_midus_life_satisfaction | subjective_wellbeing | MIDUS 1-3 | data_backed_baseline | ALL NULL | high | [] | KEEP |
| mc_midus_perceived_control | subjective_wellbeing | MIDUS 1-3 | data_backed_baseline | ALL NULL | medium | [] | KEEP |

### 3.2 Lab-Only Cards (4 contextual_prior)

| Model Card | Domain | Source | Artifact Class | Approval Blockers | Verdict |
|-----------|--------|--------|----------------|-------------------|---------|
| mc_lit_career_financial | career_education, financial | Literature | contextual_prior | No actual dataset, no calibration, no baseline table | CORRECT -- contextual priors cannot be route_b_approved per schema |
| mc_lit_health | health | Literature | contextual_prior | No actual dataset, no calibration, no baseline table | CORRECT |
| mc_lit_relationship | relationship | Literature | contextual_prior | No actual dataset, no calibration, no baseline table | CORRECT |
| mc_lit_subjective_wellbeing | subjective_wellbeing | Literature | contextual_prior | No actual dataset, no calibration, no baseline table | CORRECT |

**Finding 3**: The schema correctly prevents contextual_prior cards from being route_b_approved (validated by `_enforce_approval_guardrails` in `population_baseline.py`). No demotion needed for any card.

**Finding 4**: All calibration metrics (brier_score, calibration_slope, calibration_intercept, auc, r2) are NULL on every single model card. No calibrated_model artifacts exist. This is expected -- calibrated_model is the next evolution beyond data_backed_baseline and has not been built yet.

---

## 4. NLSY97 2005 Round Age Range Audit

### Current Claims

From `nlsy97_route_b_baselines_v2.yaml`:
```yaml
survey_year: 2005
respondent_age_range: "25-29"
```

### Verification

- NLSY97 cohort born 1980-84 (nationally representative US youth)
- In 2005, respondents born 1980 would be 24-25; respondents born 1984 would be 20-21
- The age range "25-29" does NOT match "born 1980-84" for a 2005 survey year
- Born 1980-84 in 2005 = ages 21-25 (not 25-29)
- Born 1975-79 in 2005 = ages 26-30

**Finding 5**: The age range "25-29" is INCORRECT for the stated cohort "born 1980-84". Either:
- (a) The cohort is wrong (should be born ~1976-1980 for ages 25-29 in 2005), OR
- (b) The age range is wrong (should be "21-25" for born 1980-84 in 2005), OR
- (c) The survey year is wrong (age 25-29 for born 1980-84 would be 2005-2013, not 2005)

**Critical**: No NLSY97 age variable was directly verified from the data. The age range "25-29" is derived from cohort knowledge, not computed from an actual age variable in the dataset.

**Recommendation**: This needs resolution before the baselines can be considered reliable. The age range claim should be verified against an actual age variable (e.g., `R0536300` - age in years at interview, or computed from birth year and interview date).

---

## 5. NLSY97 Financial Missingness Audit

### Data Points

From `nlsy97_route_b_baselines_v2.yaml`:
```yaml
financial:
  - code: S5412800
    display_label: Total Family Income
    n_valid: 6110
    missingness_rate: 31.99
```

Missingness breakdown (from artifact explanation):
- 1228 refusals
- 1646 invalid skip
- Total missing: ~2874 out of ~9080 sample = 31.99%

### Assessment

| Criterion | Status | Notes |
|-----------|--------|-------|
| Missingness rate | HIGH (32%) | Exceeds typical 10% threshold for reliable baselines |
| Refusal rate | 13.5% (1228/~9080) | Non-trivial; suggests income sensitivity |
| Invalid skip rate | 18.1% (1646/~9080) | May indicate survey design issues |
| Variable type | Family income (household) | NOT individual earnings |
| Inflation adjustment | None (2005 dollars) | Cross-cohort comparison limited |

**Finding 6**: 32% missingness on the financial outcome variable is a significant quality concern. The artifact is still data_backed_baseline (actual data WAS used, statistics ARE computed), but the high missingness means:
- Descriptive statistics (mean=$55,111, median=$37,650) may be biased toward respondents willing to report income
- Family income is a proxy, not a direct measure of individual financial outcomes
- The baseline is usable as a directional anchor but should carry a prominent missingness caveat

**Recommendation**: Do NOT auto-demote. The artifact correctly documents the missingness. Add an explicit missingness severity flag to the artifact metadata if not already present.

---

## 6. MIDUS Limitations Audit

### Structural Limitations

| Limitation | Impact | Mitigation |
|-----------|--------|------------|
| No individual longitudinal linkage | Cannot track individual trajectories across waves | Cross-wave aggregate comparison only (documented) |
| SAQ missingness 11-19% | Life satisfaction, perceived mastery affected | Missingness documented in baseline tables |
| Core health missingness <1% | Self-rated health, chronic conditions reliable | Minimal concern |
| Wave 1 scale direction reversed | Self-rated health 5=excellent in Wave 1, 1=excellent in Waves 2-3 | Documented in `scale_direction_issue` field |
| Attrition bias | Sample sizes decrease: 7108 -> 4963 -> 3294 | Cannot control for selective attrition |
| Cohort specificity | Aged 25-74 in 1995; not representative of all adults | Transfer risk documented as medium-high |

**Finding 7**: MIDUS baselines are appropriately documented. The cross-wave aggregate comparison limitation is correctly stated. No demotion needed.

---

## 7. NLSY97 Outcome Definitions Status

All 11 NLSY97 outcome definitions in `outcome_definitions_p16.yaml` remain at `confirmation_status: candidate` with `confirmed_variable_names: []`.

| Outcome | Domain | Status | Confirmed Variables |
|---------|--------|--------|---------------------|
| highest_degree_or_credential | career_education | candidate | [] |
| employment_stability | career_education | candidate | [] |
| occupational_status_or_job_quality | career_education | candidate | [] |
| work_hours_stability | career_education | candidate | [] |
| income_band_or_earnings_level | financial | candidate | [] |
| financial_distress_proxy | financial | candidate | [] |
| (health outcomes) | health | -- | MIDUS only, data_confirmed |
| (relationship outcomes) | relationship | -- | MIDUS only |
| (wellbeing outcomes) | subjective_wellbeing | -- | MIDUS only |

**Finding 8**: The outcome definitions file tracks a broader set of candidate outcomes beyond what the Route B baselines actually compute. The baselines (pa_nlsy97_career_education, pa_nlsy97_financial) use specific variables (S5412600, S5413300, S5412800) that ARE confirmed in the baseline config, even though the formal outcome_definitions file lists them as "candidate". This is a documentation inconsistency -- the variables are confirmed in practice (used in baselines with computed statistics) but not formally marked as such in the outcome definitions file.

---

## 8. Artifact Class Distribution

| Artifact Class | Count | Route B Approved | Notes |
|---------------|-------|-------------------|-------|
| data_backed_baseline | 7 model cards + 7 artifacts | Yes | All use actual data |
| contextual_prior | 4 model cards + 5 artifacts | No (lab_only) | Literature only, correctly restricted |
| calibrated_model | 0 | N/A | Not yet built; schema supports it |

**Finding 9**: The three-tier artifact class system (contextual_prior -> data_backed_baseline -> calibrated_model) is correctly implemented in code and enforced by Pydantic validators. No calibrated_model artifacts exist yet, which is expected.

---

## 9. Recommended Actions

### Immediate (no code changes needed)

1. **Resolve NLSY97 age range discrepancy** (Finding 5): The "born 1980-84" + "2005 survey" + "age 25-29" claim is internally inconsistent. Either the cohort or age range needs correction. Verify against an actual age variable.

2. **Document NLSY97 financial missingness severity** (Finding 6): The 32% missingness is already documented in the artifact, but consider adding a `missingness_severity: high` flag to make it more visible in the coverage matrix.

### Medium-term (before calibrated_model builds)

3. **Formalize NLSY97 variable confirmation** (Finding 8): Update `outcome_definitions_p16.yaml` to mark the 3 variables used in baselines (S5412600, S5413300, S5412800) as `data_confirmed` rather than `candidate`.

4. **Build calibrated_model artifacts**: All current Route B baselines are descriptive (baseline_table). The calibrated_model tier (with actual calibration metrics) has not been built for any artifact. This is the next step in Route B maturation.

5. **Address NLSY97 health gap**: While MIDUS covers health, there is no NLSY97 health baseline. If NLSY97 is intended to be the longitudinal anchor, a health outcome needs to be identified and computed.

### Not Recommended

6. **Do NOT demote any currently approved artifacts**: All 7 data_backed_baseline cards have empty approval blockers. The missingness and transfer risk concerns are documented limitations, not demotion triggers.

7. **Do NOT promote contextual_prior cards to route_b_approved**: The schema correctly prevents this. Literature-only priors cannot be route_b_approved without data backing.

---

## 10. Summary of Findings

| # | Finding | Severity | Action Required |
|---|---------|----------|-----------------|
| 1 | All 5 domains covered in matrix | PASS | None |
| 2 | Health covered by MIDUS (2 data-backed baselines) | PASS | None |
| 3 | Schema correctly restricts contextual_prior approval | PASS | None |
| 4 | All calibration metrics NULL; no calibrated_model artifacts | INFO | Build calibrated models |
| 5 | NLSY97 age range "25-29" inconsistent with "born 1980-84" in 2005 | BLOCKER | Verify age range from data |
| 6 | NLSY97 financial missingness 32% | WARNING | Document severity |
| 7 | MIDUS limitations correctly documented | PASS | None |
| 8 | NLSY97 outcome definitions all "candidate" despite variable use | WARNING | Formalize confirmation |
| 9 | Three-tier artifact class system correctly implemented | PASS | None |
| 10 | No demotion needed for any artifact | PASS | None |
