# Phase 16 NLSY97 Baseline Tables

**Date:** 2026-06-03
**Status:** Exploratory baseline tables generated from NLSY97 sample

## Summary

Phase 16 generated 12 baseline tables from a 50,000-row sample of the NLSY97 dataset. All tables are aggregate statistics only - no individual-level data is included.

## Generated Tables

### Demographics

| Variable | N Valid | Missingness | Distribution |
|----------|---------|-------------|--------------|
| Respondent ID | 8,984 | 0% | Unique IDs |
| Age | 8,984 | 0% | Values: 0-99 |
| Sex | 8,984 | 0% | Values: 1, 2 |
| Race/Ethnicity | 8,984 | 0% | Values: 1-5 |

### Education

| Variable | N Valid | Missingness | Distribution |
|----------|---------|-------------|--------------|
| Highest Degree | 8,984 | 0% | Values: 0-9 |
| Highest Grade | 8,984 | 0% | Values: 0-20 |
| Enrollment Status | 8,984 | 0% | Values: 0-3 |

### Employment

| Variable | N Valid | Missingness | Distribution |
|----------|---------|-------------|--------------|
| Employment Status | 8,984 | 0% | Values: 0-5 |
| Weeks Worked | 8,984 | 0% | Values: 0-52 |
| Hours Worked | 8,984 | 0% | Values: 0-99 |

### Financial

| Variable | N Valid | Missingness | Distribution |
|----------|---------|-------------|--------------|
| Personal Income | 8,984 | 0% | Values: 0-999999 |
| Household Income | 8,984 | 0% | Values: 0-999999 |

## Key Observations

1. **Zero missingness:** All 13 variables have 0% missingness in the sample
2. **Sample size:** 8,984 respondents processed (from 50,000 row sample)
3. **Variable coverage:** Demographics, education, employment, and financial domains covered

## Limitations

1. **Sample only:** 50,000 rows from full dataset (8.1GB CSV)
2. **Round 1 only:** Variables from 1997 round (R prefix)
3. **No longitudinal:** Single cross-section, not panel data
4. **No value labels:** Response codes not mapped to labels yet
5. **Exploratory only:** Not validated for production use

## Artifact Location

- **JSON:** `labs/population_baseline/artifacts/nlsy97_baseline_tables_p16.json`
- **This document:** `labs/population_baseline/P16_NLSY97_BASELINE_TABLES.md`

## Next Steps

1. **Value label extraction:** Map response codes to labels
2. **Longitudinal analysis:** Include multiple rounds
3. **Cross-wave comparison:** Compare with MIDUS patterns
