# Phase 13 — Variable Confirmation Status

## Summary

MIDUS 2 variables were verified via ICPSR's public variable search (no account required). NLSY97 variables require NLS Investigator account for verification.

**Key finding**: All `B1S*`/`B1P*` candidate variables are from **MIDUS 2** (ICPSR 04652). MIDUS 1 (ICPSR 02760) uses `A1S*`/`A1P*` prefixes for the same constructs. Big Five personality variable names needed correction (e.g., `B1SCON` → `B1SCONS`).

## Confirmation Status Definitions

| Status | Meaning |
|--------|---------|
| `candidate` | Variable name is a plausible label from documentation/training data. Not verified against actual codebook or data. |
| `metadata_confirmed` | Variable name verified against codebook or official metadata page. Name, type, and coding confirmed. |
| `data_confirmed` | Variable name verified by reading actual raw data column headers. Data exists and is readable. |
| `rejected` | Variable was a candidate but inspection revealed it does not exist or does not measure the intended construct. |

## MIDUS Variable Naming Convention

| Wave | ICPSR ID | SAQ Prefix | Phone Prefix | Example |
|------|----------|-----------|-------------|---------|
| MIDUS 1 | 02760 | `A1S*` | `A1P*` | `A1SCONS` (conscientiousness) |
| MIDUS 2 | 04652 | `B1S*` | `B1P*` | `B1SCONS` (conscientiousness) |
| MIDUS 3 | 36346 | `B3S*` | `B3P*` | (not yet verified) |

## Current Status — Features (13 total)

| Feature ID | Source | Candidate Variables | Confirmed Variables | Status | Confirmation Source | Notes |
|-----------|--------|-------------------|-------------------|--------|-------------------|-------|
| conscientiousness | MIDUS 2 | B1SCON, B1PACON | **B1SCONS1, B1SCONS2, B1PACON** | metadata_confirmed | ICPSR variable search | B1SCON rejected — actual name is B1SCONS1/B1SCONS2 |
| neuroticism | MIDUS 2 | B1SNEU, B1PANEGAFF | **B1SNEURO, B1PANEGAFF** | metadata_confirmed | ICPSR variable search | B1SNEU rejected — actual name is B1SNEURO |
| extraversion | MIDUS 2 | B1SEXT | **B1SEXTRA** | metadata_confirmed | ICPSR variable search | B1SEXT rejected — actual name is B1SEXTRA |
| agreeableness | MIDUS 2 | B1SAGR | **B1SAGREE** | metadata_confirmed | ICPSR variable search | B1SAGR rejected — actual name is B1SAGREE |
| openness | MIDUS 2 | B1SOPN | **B1SOPEN** | metadata_confirmed | ICPSR variable search | B1SOPN rejected — actual name is B1SOPEN |
| perceived_mastery | MIDUS 2 | B1SCMAS | **B1SCMAS, B1SMASTE, B1SCTRL** | metadata_confirmed | ICPSR variable search | B1SCMAS confirmed. Additional: B1SMASTE, B1SCTRL |
| education_status | NLSY97 | CV_HGC, CVC_HIGHEST_DEGREE | [] | candidate | none | Requires NLS Investigator account |
| employment_status | NLSY97 | CV_WKSTAT, EMP_STATUS | [] | candidate | none | Requires NLS Investigator account |
| financial_stability | NLSY97 | CV_INCOME_GROSS, YINC, Q13-4 | [] | candidate | none | Requires NLS Investigator account |
| relationship_status | MIDUS 2 | B1SMSTAT, B1SKINSP | **B1SMSTAT, B1SKINSP** | metadata_confirmed | ICPSR variable search | Both confirmed |
| health_constraints | MIDUS 2 | B1SA1, B1SCONDP | **B1SA1, B1SCONDP** | metadata_confirmed | ICPSR variable search | Both confirmed |
| social_support | MIDUS 2 | B1SCALL, B1SCSAT | **B1SCALL, B1SCSAT** | metadata_confirmed | ICPSR variable search | Both confirmed |
| sleep_regularity | MIDUS 2 | B1SA52A, B1SA52B | **B1SA52A** | metadata_confirmed | ICPSR variable search | B1SA52A confirmed; B1SA52B not checked |
| physical_activity | MIDUS 2 | B1SA40A, B1SA40B | **B1SA40A** | metadata_confirmed | ICPSR variable search | B1SA40A confirmed; B1SA40B not checked |

## Current Status — Outcomes (15 total)

| Outcome ID | Domain | Source | Status | Confirmation Source | Notes |
|-----------|--------|--------|--------|-------------------|-------|
| highest_degree_or_credential | career_education | NLSY97 | candidate | none | Requires NLS Investigator account |
| employment_stability | career_education | NLSY97 | candidate | none | Requires NLS Investigator account |
| occupational_status_or_job_quality | career_education | NLSY97 | candidate | none | Requires NLS Investigator account |
| work_hours_stability | career_education | NLSY97 | candidate | none | Requires NLS Investigator account |
| income_band_or_earnings_level | financial | NLSY97 | candidate | none | Requires NLS Investigator account |
| financial_distress_proxy | financial | NLSY97 | candidate | none | Requires NLS Investigator account |
| self_rated_health | health | MIDUS 2 | metadata_confirmed | ICPSR variable search | B1SA1 confirmed |
| chronic_condition_count | health | MIDUS 2 | metadata_confirmed | ICPSR variable search | B1SCHRON, B1SCHROX found |
| functional_limitation | health | MIDUS 2 | candidate | none | Variable not yet searched |
| marital_or_partner_status_stability | relationship | MIDUS 2 | metadata_confirmed | ICPSR variable search | B1SMSTAT confirmed |
| social_support_quality | relationship | MIDUS 2 | metadata_confirmed | ICPSR variable search | B1SCALL, B1SCSAT confirmed |
| social_strain | relationship | MIDUS 2 | candidate | none | Variable not yet searched |
| life_satisfaction | subjective_wellbeing | MIDUS 2 | candidate | none | Variable not yet searched |
| psychological_wellbeing | subjective_wellbeing | MIDUS 2 | metadata_confirmed | ICPSR variable search | B1SPWBE1, B1SPWBE2 found |
| depressive_symptom_proxy | subjective_wellbeing | MIDUS 2 | metadata_confirmed | ICPSR variable search | B1SA55BY, B1SA55BZ found |
| perceived_control_or_mastery | subjective_wellbeing | MIDUS 2 | metadata_confirmed | ICPSR variable search | B1SMASTE, B1SCTRL confirmed |

## NLSY97 Variables — Not Yet Verified

NLSY97 variable names (CV_HGC, CVC_HIGHEST_DEGREE, CV_WKSTAT, etc.) require verification via NLS Investigator with an authenticated account. The guest search UI was explored but the variable search form did not return results in guest mode.

**Action required**: Create NLS Investigator account and verify variable names. See P13_USER_DOWNLOAD_INSTRUCTIONS.md.

## What Changed From Phase 12

| Aspect | Phase 12 | Phase 13 |
|--------|----------|----------|
| Variable status | All candidate | 10/13 MIDUS features metadata_confirmed |
| Big Five names | B1SCON, B1SNEU, B1SEXT, B1SAGR, B1SOPN | B1SCONS, B1SNEURO, B1SEXTRA, B1SAGREE, B1SOPEN |
| Confirmation source | none | ICPSR variable search (public, no account) |
| MIDUS wave distinction | Not specified | Explicitly MIDUS 2 (ICPSR 04652) |
| NLSY97 verification | Not attempted | Attempted, blocked by account requirement |

## Transfer Risk Remains High

Even after metadata confirmation, transfer risk stays high for all variables. Confirmation only verifies the variable exists and measures the intended construct — it does NOT reduce the fundamental risk of applying population-level patterns to individual prediction.
