# Phase 16 NLSY97 Priority Variables

**Date:** 2026-06-03
**Status:** Priority variables identified from dictionary search

## Summary

Phase 16 searched the NLSY97 variable dictionary for priority constructs across 5 domains. The search found 46,548 total matches, with many variables containing keywords related to education, employment, finances, cognition, and demographics.

## Search Results by Domain

| Domain | Priority | Matches | Sample Variables |
|--------|----------|---------|------------------|
| career_education | high | 4,554 | Degree, education, school, college |
| employment | high | 29,540 | Work, hours, occupation, industry |
| financial | high | 1,379 | Income, earnings, wage, poverty |
| cognitive_non_cognitive | medium | 730 | ASVAB, AFQT, cognitive, locus |
| demographics | high | 10,345 | Age, sex, race, respondent ID |

## Priority Variables by Domain

### Career/Education (High Priority)

**Key variables identified:**
- Highest degree attained
- Highest grade completed
- Enrollment status
- College attendance
- School attendance

**Sample variables:**
- `B0002500`: PSTRAN_ANYDEGREE L1
- Variables containing "degree", "education", "school", "college"

### Employment (High Priority)

**Key variables identified:**
- Employment status
- Weeks worked
- Hours worked
- Occupation
- Industry
- Unemployment

**Sample variables:**
- `C0003500`: R WORK FOR PAY OR PROFIT LAST WEEK? COVID
- `C0003600`: HOURS R WORKED LAST WEEK AT ALL JOBS COVID
- Variables containing "work", "employment", "occupation"

### Financial (High Priority)

**Key variables identified:**
- Personal income
- Household income
- Wage/salary
- Financial hardship
- Difficulty paying bills

**Sample variables:**
- `R0144900`: AMT INCOME RCVD (END<16) L1,1 1997
- Variables containing "income", "earnings", "wage"

### Cognitive/Non-Cognitive (Medium Priority)

**Key variables identified:**
- ASVAB scores
- AFQT scores
- Cognitive ability
- Locus of control
- Self-esteem

**Sample variables:**
- `R0538900`: CAT-ASVAB!STPEL (SYMBOL) 1997
- `R0539100`: CAT-ASVAB!SPECIAL (SYMBOL) 1997
- Variables containing "ASVAB", "AFQT", "cognitive"

### Demographics (High Priority)

**Key variables identified:**
- Respondent ID
- Age
- Sex
- Race/ethnicity
- Birth year
- Survey year/round

**Sample variables:**
- `R0001000`: WHAT IS RS SEX (CRCT) 1997
- `R0001200`: CHK RS CURR AGE INCRCT INF ROST 1997
- Variables containing "sex", "age", "race"

## Limitations

1. **Too many matches:** 46,548 variables is too many to review manually
2. **Keyword ambiguity:** Many matches may be false positives
3. **No verification yet:** Variable codes not verified against CSV header
4. **Round-specific:** Many variables are round-specific (A=1997, B=1998, etc.)

## Next Steps

1. **Filter to high-confidence matches:** Reduce to manageable set
2. **Verify against CSV header:** Confirm variable codes exist in actual data
3. **Select final priority set:** Choose ~50-100 variables for baseline tables

## Output Files

- `labs/population_baseline/config/nlsy97_priority_variables_p16.yaml` - All matches
