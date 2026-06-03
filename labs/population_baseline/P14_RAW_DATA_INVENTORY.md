# Phase 14 Raw Data Inventory

**Date:** 2026-06-03
**Status:** Local ingestion complete, parser smoke checks pending (SPSS format requires pyreadstat)

## Summary

| Source | Files | Total Size | Format | Status |
|--------|-------|------------|--------|--------|
| NLSY97 | 1 ZIP archive | 454 MB | ZIP (contains CSV, DAT, CDB, SDF, SAS, R, NLSY97) | Copied |
| MIDUS 1 | 1 SPSS + 1 PDF | 44 MB | .sav + .pdf | Copied |
| MIDUS 2 | 1 SPSS + 1 PDF | 27 MB | .sav + .pdf | Copied |
| MIDUS 3 | 1 SPSS + 1 PDF | 67 MB | .sav + .pdf | Copied |

## Detailed File Inventory

### NLSY97 (National Longitudinal Survey of Youth 1997)

**Source:** ~/Downloads/nlsy97_all_1997-2023.zip
**Target:** labs/population_baseline/data/raw/nlsy97/nlsy97_all_1997-2023.zip

**ZIP Contents:**
| Filename | Size | Format |
|----------|------|--------|
| nlsy97_all_1997-2023.csv | 8.1 GB | CSV |
| nlsy97_all_1997-2023.dat | 8.1 GB | Fixed-width data |
| nlsy97_all_1997-2023.cdb | 329 MB | CDB (compressed data) |
| nlsy97_all_1997-2023.sas | 128 MB | SAS transport file |
| nlsy97_all_1997-2023.sdf | 65 MB | SDF format |
| nlsy97_all_1997-2023.R | 161 MB | R data format |
| nlsy97_all_1997-2023.NLSY97 | 2.7 MB | NLSY97 native format |

**Notes:** 
- CSV is 8.1 GB uncompressed - too large for in-memory parsing without chunking
- Contains longitudinal data from 1997-2023
- No separate codebook PDF included in archive

### MIDUS 1 (Midlife in the United States - Wave 1)

**Source Files:**
- ~/Downloads/M1_P1_SURVEY_N7108_20190116.sav → labs/population_baseline/data/raw/midus/midus1/
- ~/Downloads/M1_P1_Codebook_20220505.pdf → labs/population_baseline/data/raw/midus/midus1/codebook/

**File Details:**
| Filename | Size | Format | Description |
|----------|------|--------|-------------|
| M1_P1_SURVEY_N7108_20190116.sav | 39.6 MB | SPSS (.sav) | Project 1 Survey, N=7,108 |
| M1_P1_Codebook_20220505.pdf | 6.3 MB | PDF | Codebook documentation |

**Notes:**
- SPSS format requires pyreadstat to parse
- N=7,108 respondents
- Codebook available for variable documentation

### MIDUS 2 (Midlife in the United States - Wave 2)

**Source Files:**
- ~/Downloads/M2_P1_SURVEY_N4963_20200720.sav → labs/population_baseline/data/raw/midus/midus2/
- ~/Downloads/M2_P1_Codebook_20210129.pdf → labs/population_baseline/data/raw/midus/midus2/codebook/

**File Details:**
| Filename | Size | Format | Description |
|----------|------|--------|-------------|
| M2_P1_SURVEY_N4963_20200720.sav | 20.2 MB | SPSS (.sav) | Project 1 Survey, N=4,963 |
| M2_P1_Codebook_20210129.pdf | 8.0 MB | PDF | Codebook documentation |

**Notes:**
- SPSS format requires pyreadstat to parse
- N=4,963 respondents (follow-up to MIDUS 1)
- Codebook available for variable documentation

### MIDUS 3 (Midlife in the United States - Wave 3)

**Source Files:**
- ~/Downloads/M3_P1_SURVEY_N3294_20251029.sav → labs/population_baseline/data/raw/midus/midus3/
- ~/Downloads/M3_P1_Codebook_20251125.pdf → labs/population_baseline/data/raw/midus/midus3/codebook/

**File Details:**
| Filename | Size | Format | Description |
|----------|------|--------|-------------|
| M3_P1_SURVEY_N3294_20251029.sav | 15.4 MB | SPSS (.sav) | Project 1 Survey, N=3,294 |
| M3_P1_Codebook_20251125.pdf | 54.4 MB | PDF | Codebook documentation |

**Notes:**
- SPSS format requires pyreadstat to parse
- N=3,294 respondents (follow-up to MIDUS 2)
- Codebook available for variable documentation

## Format Analysis

### SPSS Files (.sav)
All three MIDUS datasets are in SPSS format. To parse these files, we need:
- **pyreadstat** Python package (not currently installed)
- Alternative: Convert to CSV using R or other tools

### NLSY97 ZIP Archive
The NLSY97 archive contains multiple formats:
- **CSV** (8.1 GB) - largest, but most compatible
- **DAT** (8.1 GB) - fixed-width format
- **CDB** (329 MB) - compressed format
- **SAS** (128 MB) - SAS transport format
- **SDF** (65 MB) - SDF format
- **R** (161 MB) - R data format
- **NLSY97** (2.7 MB) - native format

**Recommendation:** Use CSV for parsing, but it's 8.1 GB uncompressed. Consider chunked reading.

## Parser Status

### Existing Parsers
- `parse_nlsy97_extract.py` - Exists, needs testing
- `parse_midus_package.py` - Exists, needs testing

### Dependencies Required
- **pyreadstat** - Required for SPSS .sav files (not installed)
- Standard Python libraries for CSV parsing

## Gitignore Protection

All raw data directories are properly gitignored:
- `labs/population_baseline/data/raw/*` ✓
- `labs/population_baseline/data/processed/*` ✓
- `labs/population_baseline/artifacts/*` ✓

## Next Steps

1. **Install pyreadstat** - Required for MIDUS SPSS parsing
2. **Test parsers** - Run smoke checks on copied data
3. **Extract NLSY97 CSV** - For variable inspection (may need chunked reading)
4. **Update feature_mapping and outcome_definitions** - Based on actual file inspection
5. **Phase 15** - Variable confirmation and first baseline tables

## Safety Confirmations

- ✅ No raw data committed to git
- ✅ No raw data uploaded anywhere
- ✅ No LLM/provider called with raw data
- ✅ No production ML added
- ✅ No Route B approval granted
- ✅ All raw data in gitignored directories only
