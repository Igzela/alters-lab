# Next Decision Point

## Current Status (Phase 13 — Public Data Acquisition + Metadata Confirmation)

Phase 13 promoted the dual-source pilot from candidate planning to active data acquisition. Both NLSY97 and MIDUS require authenticated downloads (free accounts), so no raw data was fetched automatically. All variable mappings remain at **candidate** status — no codebook or raw data has been inspected yet.

## What Phase 13 Built

- **Data acquisition manifest**: `labs/population_baseline/config/data_acquisition_manifest_p13.yaml`
- **Acquisition documentation**: `P13_DATA_ACQUISITION.md`, `P13_USER_DOWNLOAD_INSTRUCTIONS.md`
- **Variable confirmation tracking**: `P13_VARIABLE_CONFIRMATION.md`, `feature_mapping_p13.yaml`, `outcome_definitions_p13.yaml` — all variables remain `candidate` with explicit `confirmation_source: none`
- **Scripts**:
  - `acquire_public_resources.py` — creates directories, checks public page availability
  - `inventory_raw_data.py` — scans raw dirs, computes checksums
  - `validate_raw_data_presence.py` — checks expected files exist
  - `parse_nlsy97_extract.py` — inspects NLSY97 CSV columns (scaffold)
  - `parse_midus_package.py` — inspects MIDUS CSV columns with key variable detection
- **Acquisition log**: `artifacts/acquisition_log_p13.json` — 6/7 public pages accessible
- **Tests**: 37 new tests (1643 total) enforcing manifest, feature, outcome, and policy invariants

## What Exists Now

- **Schemas**: `population_baseline.py` (P11) + `population_baseline_pilot.py` (P12)
- **Lab configs**: `source_selection_v0_1.yaml`, `outcome_definitions_p13.yaml`, `feature_mapping_p13.yaml`, `data_acquisition_manifest_p13.yaml`
- **Lab docs**: `P12_DATA_ACCESS_PLAN.md`, `P13_DATA_ACQUISITION.md`, `P13_USER_DOWNLOAD_INSTRUCTIONS.md`, `P13_VARIABLE_CONFIRMATION.md`
- **Scripts**: 5 acquisition/inventory/parser scripts
- **Tests**: 1643 passing (37 P13-specific)

## Current Next Decision After Phase 13

### Path A: User downloads data first (required)

1. **Create NLS Investigator account** → follow `P13_USER_DOWNLOAD_INSTRUCTIONS.md` Section 1
2. **Create ICPSR account** → follow `P13_USER_DOWNLOAD_INSTRUCTIONS.md` Section 2
3. **Download and extract** to `labs/population_baseline/data/raw/`
4. **Run inventory**: `python3 labs/population_baseline/scripts/inventory_raw_data.py`
5. **Run validation**: `python3 labs/population_baseline/scripts/validate_raw_data_presence.py`

### Path B: After data is in place

6. **Run parsers** to inspect actual column names:
   - `python3 labs/population_baseline/scripts/parse_nlsy97_extract.py --dir labs/population_baseline/data/raw/nlsy97/`
   - `python3 labs/population_baseline/scripts/parse_midus_package.py --dir labs/population_baseline/data/raw/midus/`
7. **Compare columns against candidate variables** in `feature_mapping_p13.yaml`
8. **Promote variables** from `candidate` → `metadata_confirmed` or `rejected`
9. **Build first baseline_table artifacts** — descriptive statistics for preferred outcomes
10. **Only after baseline table validation** — consider interpretable baseline models

## What Must NOT Happen Yet

- No production ML model integration
- No route_b approval granted
- No exact personal probabilities emitted
- No raw data committed to the repository
- No modification to active YAML or rubric

## Blocked On

- Manual data download (NLS Investigator + ICPSR accounts)
- Variable metadata inspection against real codebooks
- Baseline table computation and review
