# Phase 14 Variable Confirmation Preparation

**Date:** 2026-06-03
**Status:** Files ingested, codebook inspection pending, variable promotion deferred

## Summary

Phase 14 has successfully ingested raw data files into local gitignored directories. However, variable confirmation is deferred because:

1. **NLSY97**: Contains a ZIP archive with CSV/DAT files (8.1GB), but no extracted CSV files for direct parsing
2. **MIDUS**: Contains SPSS .sav files that require pyreadstat (not currently installed)

No variables have been promoted from `candidate` to `metadata_confirmed` or `data_confirmed` status.

## Current Variable Status

### From feature_mapping_p13.yaml
All variables remain at `candidate` status with `confirmation_source: none`.

### From outcome_definitions_p13.yaml
All outcomes remain at `candidate` status with `confirmation_source: none`.

## Format Compatibility

### NLSY97
- **Downloaded**: ZIP archive containing CSV, DAT, CDB, SAS, SDF, R, NLSY97 formats
- **Parser expectation**: Individual CSV files (nlsy97_core_demographics.csv, etc.)
- **Status**: Format mismatch - parser designed for pre-extracted P13 files
- **Action needed**: Either extract CSV from ZIP or modify parser to handle ZIP

### MIDUS
- **Downloaded**: SPSS .sav files
- **Parser expectation**: CSV files (midus1_saq.csv, etc.)
- **Status**: Format mismatch - requires pyreadstat or SPSS-to-CSV conversion
- **Action needed**: Install pyreadstat or use R/other tools for conversion

## Dependencies Required

### pyreadstat
- **Purpose**: Read SPSS .sav files in Python
- **Status**: Not installed
- **Installation**: `pip install pyreadstat`
- **Impact**: Required for MIDUS variable inspection and parsing

## Next Steps for Phase 15

1. **Install pyreadstat** - Required for MIDUS SPSS parsing
2. **Extract NLSY97 CSV** - Extract from ZIP archive for variable inspection
3. **Run parser smoke checks** - Against extracted/converted files
4. **Inspect codebooks** - Verify variable names against documentation
5. **Promote variables** - Update status to `metadata_confirmed` or `data_confirmed`

## Variable Promotion Rules

| Status | Condition | confirmation_source |
|--------|-----------|---------------------|
| candidate | Default state | none |
| metadata_confirmed | Codebook/metadata inspected, variable names found | codebook |
| data_confirmed | Raw data columns inspected, variable names exist in actual files | raw_data |

## Safety Confirmations

- ✅ No variables promoted without actual data inspection
- ✅ No fake confirmed_variable_names
- ✅ Confirmation sources accurate (none/codebook/metadata/raw_data)
- ✅ No raw data committed
- ✅ No production ML added
- ✅ No Route B approval granted

## Files Created

- `labs/population_baseline/config/downloaded_file_manifest_p14.yaml` - File inventory
- `labs/population_baseline/P14_RAW_DATA_INVENTORY.md` - Detailed inventory document
- `labs/population_baseline/P14_VARIABLE_CONFIRMATION_PREP.md` - This document
