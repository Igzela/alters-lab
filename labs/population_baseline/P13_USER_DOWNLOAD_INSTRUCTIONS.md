# Phase 13 — User Download Instructions

Both NLSY97 and MIDUS require authenticated accounts for data download. The acquisition script (`acquire_public_resources.py`) checks public page availability and creates directories, but cannot download the actual data files.

## What You Need To Do

### 1. NLSY97 Data Extract

**Time estimate**: 20-30 minutes

1. Register at https://www.nlsinfo.org/investigator/pages/register
2. Log in at https://www.nlsinfo.org/investigator/
3. Select "NLSY97" from the survey dropdown
4. Search for and add these variables to your extract:
   - **Demographics**: R0536300 (sex), R0536400 (race), R1482600 (age), CVC_BIRTH_DATE
   - **Education**: CV_HGC, CVC_HIGHEST_DEGREE, CVC_SCHROST_ENROLLSTAT
   - **Employment**: CV_WKSTAT, EMP_STATUS, CV_HRS_PER_WEEK
   - **Income**: CV_INCOME_GROSS, YINC, CV_INCOME_FAMILY
   - **Financial hardship**: Q13-4 series (if available)
   - **Cognitive**: ASVAB composite scores
5. Select CSV output format
6. Submit and download the extract
7. Place files in `labs/population_baseline/data/raw/nlsy97/`

### 2. MIDUS Data Packages

**Time estimate**: 15-20 minutes per study (3 studies)

1. Register at https://www.icpsr.umich.edu
2. Download each study:
   - **MIDUS I** (ICPSR 02760): https://www.icpsr.umich.edu/web/ICPSR/studies/02760
   - **MIDUS II** (ICPSR 04652): https://www.icpsr.umich.edu/web/ICPSR/studies/04652
   - **MIDUS III** (ICPSR 36346): https://www.icpsr.umich.edu/web/ICPSR/studies/36346
3. Accept terms of use for each download
4. Extract ZIPs to respective subdirectories under `labs/population_baseline/data/raw/midus/`
5. Convert SAS/Stata/SPSS files to CSV if needed (see below)

### 3. Convert Non-CSV Files (if needed)

```python
import pandas as pd

# Stata .dta → CSV
df = pd.read_stata("midus1_saq.dta")
df.to_csv("midus1_saq.csv", index=False)

# SAS .sas7bdat → CSV
df = pd.read_sas("midus1_saq.sas7bdat")
df.to_csv("midus1_saq.csv", index=False)
```

### 4. Verify Your Setup

After downloading, run:
```bash
python labs/population_baseline/scripts/inventory_raw_data.py
python labs/population_baseline/scripts/validate_raw_data_presence.py
```

## Expected Directory Structure

```
labs/population_baseline/data/raw/
├── nlsy97/
│   ├── nlsy97_core_demographics.csv
│   ├── nlsy97_education.csv
│   ├── nlsy97_employment.csv
│   ├── nlsy97_income.csv
│   ├── nlsy97_financial_hardship.csv    (optional)
│   ├── nlsy97_cognitive.csv             (optional)
│   └── codebook/
│       └── nlsy97_codebook.pdf
└── midus/
    ├── midus1/
    │   ├── midus1_saq.csv
    │   ├── midus1_phone.csv              (optional)
    │   └── codebook/
    ├── midus2/
    │   ├── midus2_saq.csv
    │   ├── midus2_phone.csv              (optional)
    │   └── codebook/
    ├── midus3/
    │   ├── midus3_saq.csv
    │   └── codebook/
    └── midus_refresher/                  (optional)
        └── midus_refresher_saq.csv
```

## Important

- **Do NOT commit** any downloaded files to git (they are gitignored)
- **Do NOT share** MIDUS data with unauthorized persons (ICPSR terms)
- Codebook PDFs help with variable confirmation but are not required for initial parsing
