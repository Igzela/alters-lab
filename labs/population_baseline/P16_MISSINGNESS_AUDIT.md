# Phase 16 Missingness Audit

**Date:** 2026-06-03
**Status:** Aggregate missingness computed for MIDUS variables

## Summary

Phase 16 audited missingness patterns across MIDUS variables and waves. All personality and wellbeing variables show moderate missingness (10-20%) due to SAQ (self-administered questionnaire) non-response.

## Missingness Summary

### Self-Rated Health (Low Missingness)

| Dataset | N Total | N Valid | Missing % | Interpretation |
|---------|---------|---------|-----------|----------------|
| MIDUS 1 | 7,108 | 7,097 | 0.15% | Acceptable |
| MIDUS 2 | 4,963 | 4,962 | 0.02% | Acceptable |
| MIDUS 3 | 3,294 | 3,293 | 0.03% | Acceptable |

**Conclusion:** Self-reported health has excellent completion rates across all waves.

### Life Satisfaction (Moderate Missingness)

| Dataset | N Total | N Valid | Missing % | Interpretation |
|---------|---------|---------|-----------|----------------|
| MIDUS 1 | 7,108 | 6,324 | 11.03% | Consider multiple imputation |
| MIDUS 2 | 4,963 | 4,040 | 18.60% | Consider multiple imputation |
| MIDUS 3 | 3,294 | 2,943 | 10.66% | Consider multiple imputation |

**Conclusion:** Life satisfaction has moderate missingness due to SAQ non-response.

### Neuroticism (Moderate Missingness)

| Dataset | N Total | N Valid | Missing % | Interpretation |
|---------|---------|---------|-----------|----------------|
| MIDUS 1 | 7,108 | 6,265 | 11.86% | Consider multiple imputation |
| MIDUS 2 | 4,963 | 4,009 | 19.22% | Consider multiple imputation |
| MIDUS 3 | 3,294 | 2,927 | 11.14% | Consider multiple imputation |

**Conclusion:** Neuroticism shows moderate missingness, highest in MIDUS 2.

### Perceived Mastery (Moderate Missingness)

| Dataset | N Total | N Valid | Missing % | Interpretation |
|---------|---------|---------|-----------|----------------|
| MIDUS 1 | 7,108 | 6,273 | 11.75% | Consider multiple imputation |
| MIDUS 2 | 4,963 | 4,016 | 19.08% | Consider multiple imputation |
| MIDUS 3 | 3,294 | 2,925 | 11.20% | Consider multiple imputation |

**Conclusion:** Perceived mastery has moderate missingness, consistent with other SAQ variables.

## Key Findings

1. **SAQ variables:** Life satisfaction, neuroticism, and perceived mastery all show 10-20% missingness
2. **Health variables:** Self-reported health has <1% missingness (asked in phone interview)
3. **Attrition:** Sample sizes decrease across waves (7,108 → 4,963 → 3,294)
4. **Missingness pattern:** SAQ non-response is the primary source of missing data

## Limitations

1. **Aggregate only:** No individual-level missingness patterns analyzed
2. **No multiple imputation:** Recommended for future analysis
3. **NLSY97 not audited:** Missingness for NLSY97 variables not computed yet
4. **No attrition analysis:** Sample shrinkage not modeled

## Recommendations

1. **For analysis:** Use multiple imputation for SAQ variables
2. **For reporting:** Report missingness rates alongside estimates
3. **For modeling:** Consider pattern-mixture models for attrition

## Output Files

- **JSON:** `labs/population_baseline/artifacts/missingness_audit_p16.json`
- **This document:** `labs/population_baseline/P16_MISSINGNESS_AUDIT.md`
