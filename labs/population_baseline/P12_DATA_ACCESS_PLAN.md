# Phase 12D — Data Access Plan

## Summary

This plan describes how to access NLSY97 and MIDUS public data. It does **not** download data. Raw data files must not be committed to the repository.

## NLSY97 Access

### How to Access
1. Go to [NLS Investigator](https://www.nlsinfo.org/investigator/)
2. Create a free account (email + institutional affiliation)
3. Select NLSY97 from the survey dropdown
4. Browse/search variables by keyword, category, or round
5. Create an extract: select variables, choose output format (CSV, SAS, SPSS, Stata)
6. Download the extract (file size varies: 100MB–1GB+ depending on variables selected)

### What Extracts Are Needed
- **Core demographics**: age, sex, race/ethnicity, region
- **Education**: highest grade, degree, enrollment status, institution type
- **Employment**: weeks worked, hours worked, occupation, industry, employment status
- **Income**: personal income, household income (multiple rounds)
- **Financial hardship**: late payments, debt collection, difficulty covering expenses
- **Cognitive/behavioral**: ASVAB scores, self-esteem, locus of control (at baseline)

### Expected Local Storage
```
labs/population_baseline/data/raw/nlsy97/
  ├── nlsy97_core_demographics.csv
  ├── nlsy97_education.csv
  ├── nlsy97_employment.csv
  ├── nlsy97_income.csv
  ├── nlsy97_financial_hardship.csv
  ├── nlsy97_cognitive.csv
  └── codebook/
      └── nlsy97_codebook.pdf
```

## MIDUS Access

### How to Access
1. Go to [ICPSR MIDUS page](https://www.icpsr.umich.edu/web/ICPSR/studies/04652)
2. Create a free ICPSR account (email + institutional affiliation)
3. Request access to MIDUS data (free for research use)
4. Download the data package (typically a ZIP with multiple files per wave)
5. MIDUS Refresher (ICPSR 04652) and Biomarker (ICPSR 29282) are separate downloads

### What Downloads Are Needed
- **MIDUS I** (ICPSR 02760): Baseline survey (1995-1996)
- **MIDUS II** (ICPSR 04652): First follow-up (2004-2006)
- **MIDUS III** (ICPSR 36346): Second follow-up (2013-2014)
- **Key files**: Main survey (SAQ), phone interview, daily diary (if available)

### Expected Local Storage
```
labs/population_baseline/data/raw/midus/
  ├── midus1/
  │   ├── midus1_saq.csv
  │   ├── midus1_phone.csv
  │   └── codebook/
  ├── midus2/
  │   ├── midus2_saq.csv
  │   ├── midus2_phone.csv
  │   └── codebook/
  ├── midus3/
  │   ├── midus3_saq.csv
  │   └── codebook/
  └── midus_refresher/
      └── ...
```

## What Must NOT Be Committed

- Raw data files (CSV, SAS, SPSS, Stata exports)
- Codebook PDFs (large, not diffable)
- Extract definitions (NLS Investigator URLs are fine in docs)
- Any file containing individual-level responses

## .gitignore Updates

```
labs/population_baseline/data/raw/*
labs/population_baseline/data/processed/*
labs/population_baseline/artifacts/*
!labs/population_baseline/data/raw/.gitkeep
!labs/population_baseline/data/processed/.gitkeep
!labs/population_baseline/artifacts/.gitkeep
```

## Privacy / License / Terms

### NLSY97
- Public use data: no restrictions on use or redistribution
- Must cite: Bureau of Labor Statistics, National Longitudinal Survey of Youth 1997
- Restricted-use data requires separate application (not needed for this pilot)

### MIDUS
- ICPSR terms: data for research use only, not for commercial purposes
- Must cite: MIDUS (Midlife in the United States) study, funded by NIA
- Data should not be shared with unauthorized persons
- Individual-level data should not be published or made publicly available

## Reproducibility Checklist

- [ ] NLSY97 extract variables documented with NLS Investigator URL
- [ ] MIDUS ICPSR study IDs documented
- [ ] Variable-to-feature mapping documented in feature_mapping_p12.yaml
- [ ] Extract creation date recorded
- [ ] Codebook versions noted
- [ ] Processing scripts (if any) committed to repo
- [ ] Raw data files in .gitignore
- [ ] Processed data files in .gitignore
- [ ] Artifact files in .gitignore
- [ ] .gitkeep files created for empty directories
