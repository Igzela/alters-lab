# Phase 13 — Data Acquisition Plan

## Summary

Phase 13 promotes the Phase 12 dual-source pilot from candidate planning to active data acquisition. Both NLSY97 and MIDUS require authenticated downloads (free accounts), so no raw data is fetched automatically by the codebase. This document provides exact manual download instructions.

## Automatic vs Manual

| Action | Automated? | Notes |
|--------|-----------|-------|
| Create raw directories | Yes | `acquire_public_resources.py` creates dirs + .gitkeep |
| Fetch public metadata pages | Yes | Script checks NLS Investigator / ICPSR page availability |
| Download NLSY97 extract | **No** | Requires NLS Investigator account + interactive variable selection |
| Download MIDUS packages | **No** | Requires ICPSR account + terms acceptance per study |
| Inventory local files | Yes | `inventory_raw_data.py` scans raw dirs |
| Validate file presence | Yes | `validate_raw_data_presence.py` checks against manifest |

## NLSY97 — Manual Download Steps

### Prerequisites
- Email address for free NLS Investigator account

### Steps

1. **Register**: Go to https://www.nlsinfo.org/investigator/pages/register and create an account.

2. **Log in**: Go to https://www.nlsinfo.org/investigator/ and log in.

3. **Select dataset**: Choose "NLSY97" from the survey dropdown.

4. **Create extract with these variable groups**:

   **Core Demographics** (required):
   - `R0536300` — Sex
   - `R0536400` — Race/ethnicity
   - `R1482600` — Age at first interview
   - `CVC_BIRTH_DATE` — Birth date
   - `CVC_HH_NET` — Household net worth (context)

   **Education** (required):
   - `CV_HGC` — Highest grade completed (each round)
   - `CVC_HIGHEST_DEGREE` — Highest degree attained
   - `CVC_SCHROST_ENROLLSTAT` — School enrollment status

   **Employment** (required):
   - `CV_WKSTAT` — Employment status (each round)
   - `EMP_STATUS` — Employment status category
   - `CV_HRS_PER_WEEK` — Hours worked per week
   - `CV_JOB_NUM` — Number of jobs held

   **Income** (required):
   - `CV_INCOME_GROSS` — Total gross income
   - `YINC` — Income from employment
   - `CV_INCOME_FAMILY` — Family income

   **Financial Hardship** (optional):
   - `Q13-4` series — Financial difficulty items (availability varies by round)
   - Late payments, debt collection, bankruptcy indicators

   **Cognitive/Non-cognitive** (optional):
   - `ASVAB_MATH_VERBAL` — ASVAB composite score
   - Self-esteem and locus of control items (baseline round)

5. **Select output format**: CSV.

6. **Submit extract**: The system will build your extract (may take minutes for large selections).

7. **Download**: Download the ZIP file containing data + codebook.

8. **Extract to**:
   ```
   labs/population_baseline/data/raw/nlsy97/
     ├── nlsy97_core_demographics.csv
     ├── nlsy97_education.csv
     ├── nlsy97_employment.csv
     ├── nlsy97_income.csv
     ├── nlsy97_financial_hardship.csv    (optional)
     ├── nlsy97_cognitive.csv             (optional)
     └── codebook/
         └── nlsy97_codebook.pdf
   ```

   **Note**: NLS Investigator produces a single extract file. You may need to split by variable group or keep as one file and rename accordingly. The parser scripts accept either format.

## MIDUS — Manual Download Steps

### Prerequisites
- Email address for free ICPSR account (institutional affiliation helps but is not required)

### Steps

1. **Register**: Go to https://www.icpsr.umich.edu and create an account.

2. **Download MIDUS I** (ICPSR 02760):
   - Navigate to: https://www.icpsr.umich.edu/web/ICPSR/studies/02760
   - Accept terms of use
   - Download the data package (ZIP)
   - Extract to: `labs/population_baseline/data/raw/midus/midus1/`
   - Convert SAS/Stata/SPSS files to CSV if not already CSV
   - Place codebook in: `labs/population_baseline/data/raw/midus/midus1/codebook/`

3. **Download MIDUS II** (ICPSR 04652):
   - Navigate to: https://www.icpsr.umich.edu/web/ICPSR/studies/04652
   - Accept terms of use
   - Download and extract to: `labs/population_baseline/data/raw/midus/midus2/`
   - Place codebook in: `labs/population_baseline/data/raw/midus/midus2/codebook/`

4. **Download MIDUS III** (ICPSR 36346):
   - Navigate to: https://www.icpsr.umich.edu/web/ICPSR/studies/36346
   - Accept terms of use
   - Download and extract to: `labs/population_baseline/data/raw/midus/midus3/`
   - Place codebook in: `labs/population_baseline/data/raw/midus/midus3/codebook/`

5. **(Optional) MIDUS Refresher** (same package as MIDUS II):
   - Included in the MIDUS II download (ICPSR 04652)
   - Extract to: `labs/population_baseline/data/raw/midus/midus_refresher/`

### Expected file formats
ICPSR packages typically include SAS (.sas7bdat), Stata (.dta), SPSS (.sav), and sometimes CSV. If CSV is not included, use Python (pandas) or R to convert:
```python
import pandas as pd
df = pd.read_stata("path/to/file.dta")
df.to_csv("path/to/file.csv", index=False)
```

## After Download

Once files are in place:

1. **Inventory**: Run `python labs/population_baseline/scripts/inventory_raw_data.py`
2. **Validate**: Run `python labs/population_baseline/scripts/validate_raw_data_presence.py`
3. **Parse**: Run parser scripts to inspect columns:
   - `python labs/population_baseline/scripts/parse_nlsy97_extract.py --dir labs/population_baseline/data/raw/nlsy97/`
   - `python labs/population_baseline/scripts/parse_midus_package.py --dir labs/population_baseline/data/raw/midus/`
4. **Confirm variables**: Compare actual column names against candidate variable labels in feature_mapping_p12.yaml
5. **Promote mappings**: Update feature_mapping_p13.yaml with confirmed variable names

## Privacy / License Summary

| Source | License | Key Restrictions |
|--------|---------|-----------------|
| NLSY97 | Public use | Cite BLS/NLS. No restrictions on use/redistribution. |
| MIDUS | ICPSR terms | Research use only. No commercial use. Don't share with unauthorized persons. |

## What Must NOT Be Committed

- Raw CSV/SAS/Stata/SPSS files
- Codebook PDFs
- ZIP archives
- Any file with individual-level responses
- NLS Investigator extract definitions (URLs in docs are fine)
