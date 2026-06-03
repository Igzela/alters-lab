# Next Decision Point

## Current Status (Phase 16 — NLSY97 Variable Mapping + Cross-Wave Analysis Complete)

Phase 16 has been completed locally. NLSY97 variable dictionary extracted, MIDUS cross-wave analysis and missingness audit done, Route B readiness reviewed.

## What Phase 16 Built

- **NLSY97 variable dictionary**: Extracted 305,325 variable labels from SAS/R files in ZIP archive
- **NLSY97 priority variables**: 46,548 priority variable headers verified
- **NLSY97 baseline tables**: Aggregate tables generated for NLSY97 outcomes
- **MIDUS cross-wave analysis**: Trajectories across waves 1-3 analyzed
- **MIDUS missingness audit**: SAQ non-response patterns assessed
- **Route B readiness review**: Integration readiness evaluated (not yet approved)

## What Exists Now

- **Scripts** (12 total):
  - `inspect_nlsy97_archive.py` - ZIP inspection without extraction
  - `parse_nlsy97_streaming.py` - Streaming CSV parser
  - `extract_nlsy97_variable_dictionary.py` - Variable label extraction
  - `search_nlsy97_variables.py` - Variable search utility
  - `build_nlsy97_baseline_tables.py` - NLSY97 aggregate table builder
  - `parse_midus_sav.py` - SPSS .sav parser with pyreadstat
  - `build_baseline_tables.py` - Aggregate table builder
  - `analyze_midus_cross_wave.py` - Cross-wave trajectory analysis
  - `analyze_missingness_p16.py` - Missingness pattern analysis
  - Plus P13 scripts (`inventory_raw_data.py`, `validate_raw_data_presence.py`)
- **Configs**: P14/P15/P16 feature mappings, outcome definitions, baseline tables, variable dictionaries
- **Artifacts**: P13-P16 artifacts including baseline tables, summaries, variable dictionaries, cross-wave analysis, missingness audit
- **Raw data** (gitignored, not committed):
  - NLSY97: 454MB ZIP (15.8GB uncompressed)
  - MIDUS 1/2/3: 39.6MB + 20.2MB + 15.4MB SPSS files

## Phase 16 Completion Summary

- ✅ NLSY97 variable dictionary extracted (305k labels)
- ✅ NLSY97 priority variables verified (46k headers)
- ✅ NLSY97 baseline tables generated
- ✅ MIDUS cross-wave analysis complete
- ✅ MIDUS missingness audit complete
- ✅ Route B readiness reviewed (NOT approved)
- ✅ No individual-level data committed
- ✅ No production ML added
- ✅ No Route B approval granted

## What's NOT Done Yet

- **Route B approval**: Public priors not approved for integration into forecast path
- **Production integration**: No `approved_for_route_b` flags set to true
- **Missingness imputation**: Analysis done, strategies not yet implemented
- **Cross-source harmonization**: MIDUS and NLSY97 not yet linked

## Next Phase: Phase 17 — Route B Integration Decision

### Required Steps

1. **Route B approval gate**
   - Review readiness review findings
   - Decide: approve, conditionally approve, or reject Route B integration
   - If approved: set `approved_for_route_b: true` on specific priors

2. **Hybrid forecast integration**
   - Route A (personal evidence) + Route B (population priors)
   - Display both sources separately in BranchForecast page
   - Implement transfer risk labeling

3. **Calibration divergence enhancement**
   - Use population priors to contextualize personal calibration divergence
   - Add cross-source comparison to divergence analysis

4. **Missingness handling**
   - Implement imputation strategy for key variables
   - Document impact on longitudinal analyses

## What Must NOT Happen Yet

- No exact personal probabilities emitted
- No raw data committed to the repository
- No modification to active YAML or rubric
- No Route B priors used in forecasts without explicit approval

## Architecture Status

- Backend: 1749 tests passing (FastAPI + Pydantic + YAML I/O)
- Frontend: 78 tests passing (React + TypeScript + Vitest)
- Data layer: DataRepo with transaction support, 16 product areas
- Type contract: OpenAPI → TypeScript auto-generation
- CI: GitHub Actions (backend tests + frontend test + build)
