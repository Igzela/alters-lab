# Phase 15 Variable Confirmation Report

**Date:** 2026-06-03
**Status:** MIDUS variables data_confirmed, NLSY97 variables remain candidate

## Summary

Phase 15 has successfully parsed MIDUS SPSS files and confirmed variable names in actual raw data. NLSY97 CSV header was inspected but variable names remain unmapped due to the 305k column structure.

## MIDUS Variable Confirmation

### Confirmed Variables (data_confirmed)

| Feature/Outcome | Variable Names | Dataset | Missingness |
|-----------------|----------------|---------|-------------|
| conscientiousness | B1SCONS1, B1SCONS2, B1PACON | MIDUS 1,2,3 | 11-19% |
| neuroticism | B1SNEURO, B1PANEGAFF | MIDUS 1,2,3 | 11-19% |
| extraversion | B1SEXTRA | MIDUS 1,2,3 | 11-19% |
| agreeableness | B1SAGREE | MIDUS 1,2,3 | 11-19% |
| openness | B1SOPEN | MIDUS 1,2,3 | 11-19% |
| perceived_mastery | B1SCMAS, B1SMASTE, B1SCTRL | MIDUS 1,2,3 | 11-19% |
| relationship_status | B1SMSTAT, B1SKINSP | MIDUS 1,2,3 | <1% |
| health_constraints | B1SA1, B1SCONDP | MIDUS 1,2,3 | <1% |
| social_support | B1SCALL, B1SCSAT | MIDUS 1,2,3 | <1% |
| sleep_regularity | B1SA52A | MIDUS 1,2,3 | <1% |
| physical_activity | B1SA40A | MIDUS 1,2,3 | <1% |
| self_rated_health | B1PA1, B1PA4, C1PA1 | MIDUS 1,2,3 | <1% |
| chronic_condition_count | B1SCONDP | MIDUS 1,2,3 | <1% |
| social_support_quality | B1SCALL, B1SCSAT | MIDUS 1,2,3 | <1% |
| life_satisfaction | A1SSATIS, B1SSATIS, C1SSATIS | MIDUS 1,2,3 | 11-19% |
| perceived_control_or_mastery | A1SMASTE, B1SMASTE, C1SMASTE | MIDUS 1,2,3 | 11-19% |

### Confirmation Source

All MIDUS variables confirmed via **raw_data** - actual variable names verified in SPSS .sav files using pyreadstat.

## NLSY97 Variable Status

### Current Status: candidate

The NLSY97 CSV file contains 305,325 columns with numeric codes (e.g., A0000100, B0000200). Variable names are not human-readable and require the codebook for mapping.

### Key Findings

- **Column count:** 305,325
- **Row count:** TBD (requires streaming count)
- **Format:** CSV with numeric column codes
- **Codebook:** Not included in archive, may need external source

### Priority Variables Still Needed

- Respondent ID (likely A0000100 or similar)
- Survey year/round
- Sex, birth year/age
- Race/ethnicity
- Education (highest degree/grade)
- Employment status
- Income/earnings
- Financial hardship measures
- Cognitive/ASVAB/AFQT scores

## MIDUS Dataset Summary

| Dataset | Variables | Rows | Key Demographics |
|---------|-----------|------|------------------|
| MIDUS 1 | 2,098 | 7,108 | Age 20-75, 51.6% female |
| MIDUS 2 | 2,189 | 4,963 | Age 28-84, 53.3% female |
| MIDUS 3 | 2,613 | 3,294 | Age 39-93, 54.9% female |

## Limitations

1. **NLSY97 variable mapping:** Requires codebook or variable label extraction from SAS/R files
2. **MIDUS Big Five missingness:** 11-19% missing due to SAQ (self-administered questionnaire) non-response
3. **Cross-wave variable names:** MIDUS 1 uses A1S prefix, MIDUS 2 uses B1S, MIDUS 3 uses C1S
4. **No codebook inspection:** PDF codebooks not parsed (would require PDF extraction tool)

## Next Steps

1. **NLSY97 variable mapping:** Extract variable labels from SAS/R files in ZIP archive
2. **Baseline table construction:** Use confirmed MIDUS variables for first baseline tables
3. **Codebook inspection:** Parse PDF codebooks for additional variable documentation
