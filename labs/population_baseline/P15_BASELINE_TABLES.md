# Phase 15 Baseline Tables

**Date:** 2026-06-03
**Status:** Exploratory baseline tables generated, no ML integration

## Summary

Phase 15 has generated 17 baseline tables from MIDUS datasets. These are aggregate statistics only - no individual-level data is included. All tables have `approved_for_route_b: false`.

## Generated Tables

### MIDUS 1 (N=7,108)

| Table | Variable | N Valid | Missingness | Mean/Rate |
|-------|----------|---------|-------------|-----------|
| self_rated_health | B1PA4 | 7,097 | 0.15% | 3.53 (scale 1-5) |
| life_satisfaction | A1SSATIS | 6,324 | 11.03% | 7.70 (scale 0-10) |
| big5_neuroticism | A1SNEURO | 6,265 | 11.86% | 2.24 (scale 1-4) |
| perceived_mastery | A1SMASTE | 6,273 | 11.75% | 5.84 (scale 1-7) |
| demographics_age | A1PAGE_M2 | 7,049 | 0.83% | 46.38 years |
| demographics_sex | A1PRSEX | 7,106 | 0.03% | 51.6% female |

### MIDUS 2 (N=4,963)

| Table | Variable | N Valid | Missingness | Mean/Rate |
|-------|----------|---------|-------------|-----------|
| self_rated_health | B1PA1 | 4,962 | 0.02% | 2.46 (scale 1-5) |
| life_satisfaction | B1SSATIS | 4,040 | 18.6% | 7.76 (scale 0-10) |
| big5_neuroticism | B1SNEURO | 4,009 | 19.22% | 2.07 (scale 1-4) |
| perceived_mastery | B1SMASTE | 4,016 | 19.08% | 5.74 (scale 1-7) |
| demographics_age | B1PAGE_M2 | 4,962 | 0.02% | 55.43 years |
| demographics_sex | B1PRSEX | 4,963 | 0.0% | 53.3% female |

### MIDUS 3 (N=3,294)

| Table | Variable | N Valid | Missingness | Mean/Rate |
|-------|----------|---------|-------------|-----------|
| self_rated_health | C1PA1 | 3,293 | 0.03% | 2.57 (scale 1-5) |
| life_satisfaction | C1SSATIS | 2,943 | 10.66% | 7.78 (scale 0-10) |
| big5_neuroticism | C1SNEURO | 2,927 | 11.14% | 2.06 (scale 1-4) |
| perceived_mastery | C1SMASTE | 2,925 | 11.2% | 5.60 (scale 1-7) |
| demographics_age | C1PRAGE | 3,294 | 0.0% | 63.64 years |
| demographics_sex | C1PRSEX | 3,294 | 0.0% | 54.9% female |

## Key Observations

### Health Outcomes
- Self-rated health is relatively stable across waves (mean ~2.5-3.5 on 1-5 scale)
- Low missingness (<1%) for health variables

### Subjective Wellbeing
- Life satisfaction consistently high (mean ~7.7-7.8 on 0-10 scale)
- Higher missingness (10-19%) due to SAQ non-response

### Personality Traits
- Neuroticism scores relatively low (mean ~2.0-2.2 on 1-4 scale)
- ~11-19% missing due to SAQ non-response

### Demographics
- Age increases across waves as expected (longitudinal cohort)
- Slight female majority in all waves (~51-55%)

## Limitations

1. **Exploratory only:** These tables are for baseline understanding, not production use
2. **No NLSY97 tables:** Variable mapping not yet completed for NLSY97
3. **Scale differences:** Some variables use different scales across waves
4. **Missing data:** Big Five and life satisfaction have 11-19% missingness
5. **No confidence intervals:** Not yet implemented
6. **No Route B approval:** All tables have `approved_for_route_b: false`

## Artifact Location

- **JSON:** `labs/population_baseline/artifacts/baseline_tables_p15.json`
- **Individual summaries:** `labs/population_baseline/artifacts/midus{1,2,3}_summary_p15.json`

## Next Steps

1. **NLSY97 baseline tables:** Complete variable mapping first
2. **Cross-wave analysis:** Compare trajectories across MIDUS waves
3. **Missingness analysis:** Understand patterns of SAQ non-response
4. **Confidence intervals:** Add proper statistical uncertainty measures
