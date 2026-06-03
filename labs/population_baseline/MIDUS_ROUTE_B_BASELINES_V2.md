# MIDUS Route B Baselines v2

## Summary

Data-backed population baseline tables for **health**, **relationship**, and **subjective_wellbeing** domains, derived from actual MIDUS data (3 waves, 1995-2014).

## Data Source

- **Dataset**: Midlife in the United States (MIDUS)
- **Waves**: MIDUS 1 (1995-96), MIDUS 2 (2004-06), MIDUS 3 (2013-14)
- **Sample Sizes**: Wave 1: N=7,108 | Wave 2: N=4,963 | Wave 3: N=3,294
- **Source Files**: SPSS .sav files confirmed via pyreadstat
- **Data Access**: ICPSR (restricted use contract)

## Domain Coverage

### health

| Variable | Wave 1 Code | Wave 2 Code | Wave 3 Code | Scale |
|---|---|---|---|---|
| Self-Rated Health | A1PA4 | B1PA1 | C1PA1 | 1=excellent, 5=poor |
| Chronic Conditions | A1SCONDP | B1SCONDP | C1SCONDP | Count (0-27) |

**Cross-Wave Summary (Self-Rated Health):**
| Wave | Year | n_valid | Missingness | Mean | Median |
|---|---|---|---|---|---|
| MIDUS 1 | 1995-96 | 7,097 | 0.15% | 3.53 | 4 |
| MIDUS 2 | 2004-06 | 4,962 | 0.02% | 2.46 | 2 |
| MIDUS 3 | 2013-14 | 3,293 | 0.03% | 2.57 | 2 |

**Note**: Scale direction change between waves (Wave 1: 5=excellent; Waves 2-3: 1=excellent). Cross-wave comparison requires direction reversal.

**Value Labels (Self-Rated Health, Waves 2-3):**
| Code | Label |
|---|---|
| 1 | Excellent |
| 2 | Very good |
| 3 | Good |
| 4 | Fair |
| 5 | Poor |

### relationship

| Variable | Wave 1 Code | Wave 2 Code | Wave 3 Code | Scale |
|---|---|---|---|---|
| Social Support | B1SCALL | — | — | Composite scale |
| Social Satisfaction | B1SCSAT | — | — | Composite scale |

**Cross-Wave Summary (Social Support, MIDUS 2 only):**
| Variable | n_valid | Missingness | Mean | Scale Range |
|---|---|---|---|---|
| B1SCALL | 4,769 | 3.9% | ~3.5 | 1-4 |
| B1SCSAT | 4,761 | 4.1% | ~3.4 | 1-4 |

**Note**: Social support variables only available in MIDUS 2 SAQ. No direct cross-wave comparison possible for this construct.

### subjective_wellbeing

| Variable | Wave 1 Code | Wave 2 Code | Wave 3 Code | Scale |
|---|---|---|---|---|
| Life Satisfaction | A1SSATIS | B1SSATIS | C1SSATIS | 0-10 |
| Perceived Mastery | A1SMASTE | B1SMASTE | C1SMASTE | 1-7 |
| Psychological Wellbeing | — | B1SPWBG | C1SPWBG | Composite |

**Cross-Wave Summary (Life Satisfaction):**
| Wave | Year | n_valid | Missingness | Mean | Median |
|---|---|---|---|---|---|
| MIDUS 1 | 1995-96 | 6,324 | 11.03% | 7.70 | 7.88 |
| MIDUS 2 | 2004-06 | 4,040 | 18.6% | 7.76 | 8.0 |
| MIDUS 3 | 2013-14 | 2,798 | 15.1% | 7.75 | 8.0 |

**Cross-Wave Summary (Perceived Mastery):**
| Wave | Year | n_valid | Missingness | Mean | Median |
|---|---|---|---|---|---|
| MIDUS 1 | 1995-96 | 6,273 | 11.75% | 5.84 | 6.0 |
| MIDUS 2 | 2004-06 | 4,061 | 18.3% | 5.60 | 5.71 |
| MIDUS 3 | 2013-14 | 2,811 | 14.7% | 5.60 | 5.71 |

**Value Labels (Life Satisfaction):**
| Scale | Meaning |
|---|---|
| 0 | Worst possible life |
| 10 | Best possible life |

**Value Labels (Perceived Mastery, Pearlin Mastery Scale):**
| Scale | Meaning |
|---|---|
| 1 | Strongly disagree |
| 7 | Strongly agree |

## Missingness Audit

| Variable | Wave 1 | Wave 2 | Wave 3 | Pattern |
|---|---|---|---|---|
| Self-Rated Health | 0.15% | 0.02% | 0.03% | Excellent (<1%) |
| Chronic Conditions | 0.15% | 0.02% | 0.03% | Excellent (<1%) |
| Life Satisfaction | 11.03% | 18.6% | 15.1% | Moderate (SAQ non-response) |
| Perceived Mastery | 11.75% | 18.3% | 14.7% | Moderate (SAQ non-response) |
| Social Support | N/A | 3.9% | N/A | Low (MIDUS 2 only) |

**Missingness Interpretation:**
- Health variables: <1% missing — excellent data quality
- SAQ variables (life satisfaction, mastery): 11-19% missing — typical for self-administered questionnaires
- Higher missingness in Wave 2 likely due to longer SAQ burden

## Cross-Wave Comparability

### Stable Constructs
- **Life Satisfaction**: Stable across waves (7.70 → 7.76 → 7.75), suggesting reliable measurement
- **Perceived Mastery**: Slight decline (5.84 → 5.60), may reflect aging or cohort effects

### Scale Direction Issues
- **Self-Rated Health**: Wave 1 uses reverse coding (5=excellent) vs Waves 2-3 (1=excellent). Must reverse for cross-wave comparison.
- **Chronic Conditions**: Consistent counting method across waves

### Attrition
- Wave 1 → 2: 30% attrition (7,108 → 4,963)
- Wave 2 → 3: 34% attrition (4,963 → 3,294)
- Survivors may be healthier/wealthier (healthy survivor bias)

## Limitations

1. **Cohort specificity**: MIDUS 1 respondents aged 25-74 in 1995; not representative of younger generations
2. **SAQ non-response**: 11-19% missingness on subjective measures
3. **Cross-wave aggregate only**: No individual longitudinal linkage in these tables
4. **Attrition bias**: Surviving respondents may differ from dropouts
5. **Self-report bias**: All measures are self-reported
6. **Scale direction**: Self-rated health scale reversed between Wave 1 and later waves
7. **Social support**: Only measured in MIDUS 2, no cross-wave comparison

## Transfer Risk

**MEDIUM** for health and subjective_wellbeing (stable constructs, good data quality).
**HIGH** for relationship (single-wave measurement, construct complexity).

## Route B Approval Status

These baselines qualify as `data_backed_baseline` artifacts:
- [x] Actual data used (SPSS files confirmed via pyreadstat)
- [x] Variable codes confirmed in raw data
- [x] Value labels documented
- [x] Missingness audited
- [x] Cross-wave comparability assessed
- [ ] Validation metrics (future: compare to other datasets)

## Safety Confirmations

- No raw data committed to repository
- No individual-level data in outputs
- No personal probabilities emitted
- No life_score created
- Aggregate statistics only
