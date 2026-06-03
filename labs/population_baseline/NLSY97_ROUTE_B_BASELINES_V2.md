# NLSY97 Route B Baselines v2

## Summary

Data-backed population baseline tables for **career_education** and **financial** domains, derived from actual NLSY97 data (2005 round, respondents aged 25-29).

## Data Source

- **Dataset**: National Longitudinal Survey of Youth 1997 (NLSY97)
- **Survey Year**: 2005 (Round 9)
- **Respondent Age**: 25-29 years old (born 1980-84)
- **Sample Size**: 50,000 rows streamed from 8.1GB CSV (89,814 total respondents)
- **Source File**: `nlsy97_all_1997-2023.zip` (454MB compressed)

## Variables

### career_education

| Variable | Code | n_valid | Missingness | Key Findings |
|---|---|---|---|---|
| Highest Grade Completed | S5412600 | 7,271 | 19.07% | Mean=12.96, Median=12 (HS grad) |
| Highest Degree Ever Received | S5413300 | 7,317 | 18.56% | 60% HS diploma, 12% Bachelor's |

**Degree Distribution (2005):**
- None: 13.1% (956)
- GED: 5.3% (388)
- High school diploma: 59.9% (4,384)
- Associate degree: 4.8% (354)
- Bachelor's degree: 12.1% (883)
- Master's degree: 3.1% (226)
- Doctorate: 0.7% (49)
- Professional degree: 1.0% (77)

### financial

| Variable | Code | n_valid | Missingness | Key Findings |
|---|---|---|---|---|
| Total Family Income | S5412800 | 6,110 | 31.99% | Mean=$55,111, Median=$37,650 |

**Income Distribution (2005):**
- $0: 2.0% (121)
- $1-$9,999: 13.1% (800)
- $10,000-$24,999: 19.3% (1,178)
- $25,000-$49,999: 26.6% (1,624)
- $50,000-$74,999: 15.1% (920)
- $75,000-$99,999: 10.7% (654)
- $100,000-$149,999: 7.6% (467)
- $150,000+: 5.7% (346)

## Value Labels

### Highest Degree (S5413300)
| Code | Label |
|---|---|
| 0 | None |
| 1 | GED |
| 2 | High school diploma |
| 3 | Associate degree |
| 4 | Bachelor's degree |
| 5 | Master's degree |
| 6 | Doctorate |
| 7 | Professional degree |

### NLSY97 Missing Value Codes
| Code | Meaning |
|---|---|
| -1 | Not in universe |
| -2 | Don't know |
| -3 | Refuse |
| -4 | Valid skip |
| -5 | Invalid skip |

## Missingness Audit

| Variable | n_total | n_valid | n_missing | Rate |
|---|---|---|---|---|
| Highest Grade | 8,984 | 7,271 | 1,713 | 19.07% |
| Highest Degree | 8,984 | 7,317 | 1,667 | 18.56% |
| Family Income | 8,984 | 6,110 | 2,874 | 31.99% |

**Missingness Patterns:**
- Education variables: ~19% missing — likely due to survey non-response in 2005 round
- Income: 32% missing — higher due to income sensitivity; standard for survey data

## Limitations

1. **Cohort specificity**: Respondents born 1980-84; transfer to other generations requires caution
2. **Family income**: Household-level, not individual earnings
3. **2005 snapshot**: No longitudinal follow-up linked in this table
4. **Self-reported**: All values are self-reported survey responses
5. **No inflation adjustment**: 2005 dollars, not adjusted to current value
6. **Sample**: 50K rows from full dataset; aggregate statistics only

## Transfer Risk

**HIGH** — Cohort-specific data from 2005. Modern populations may differ in education distribution (more college attendance), income levels (inflation, economic changes), and employment patterns.

## Route B Approval Status

These baselines are **candidates** for Route B approval as `data_backed_baseline` artifacts. Approval requires:
- [x] Actual data used (not literature-only)
- [x] Variable codes confirmed in raw data
- [x] Value labels documented
- [x] Missingness audited
- [ ] Validation metrics (future: compare to other datasets)
- [ ] Model card created

## Safety Confirmations

- No raw data committed to repository
- No individual-level data in outputs
- No personal probabilities emitted
- No life_score created
- Aggregate statistics only
