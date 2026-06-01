# Next Decision Point

## Current Status (Phase 12 — Dual-Source Public Baseline Pilot)

Phase 12 builds the first auditable public baseline pilot using MIDUS + NLSY97. No production ML model has been trained. No datasets have been downloaded yet. The lab remains inside `labs/population_baseline/` with no production integration.

## What Phase 12 Built

- **Source selection**: MIDUS and NLSY97 included; FFCWS and PSID deferred
- **17 candidate outcomes** across 5 domains (career_education, financial, health, relationship, subjective_wellbeing)
- **15 feature mappings** from MIDUS/NLSY97 variables to internal predictor_profile and behavior_metric fields
- **Data access plan** for NLSY Investigator and ICPSR (no downloads yet)
- **Baseline artifact design**: baseline_table (descriptive) + model_card_candidate (placeholder)
- **Lab-only schemas**: PopulationBaselineSourceSelection, BaselineOutcomeCandidate, BaselineFeatureCandidate, BaselineTableArtifact
- **Tests**: 25 tests enforcing source selection, outcome, feature, and artifact invariants

## What Exists Now

- **Schemas**: `apps/api/src/alters_lab/schemas/population_baseline.py` (Phase 11) + `population_baseline_pilot.py` (Phase 12)
- **Contract**: `apps/api/src/alters_lab/schemas/public_prior_contract.py`
- **Lab configs**: `labs/population_baseline/config/source_selection_v0_1.yaml`, `outcome_definitions_p12.yaml`, `feature_mapping_p12.yaml`, `baseline_artifact_schema_p12.yaml`
- **Lab docs**: `labs/population_baseline/P12_SOURCE_SELECTION.md`, `P12_OUTCOME_DEFINITIONS.md`, `P12_FEATURE_MAPPING.md`, `P12_DATA_ACCESS_PLAN.md`, `P12_BASELINE_ARTIFACT_DESIGN.md`
- **Validation standard**: `docs/VALIDATION_STANDARD.md` defines 6 gates

## Current Next Decision After Phase 12

1. **Download/prepare MIDUS and NLSY97 extracts manually** — follow the data access plan in `labs/population_baseline/P12_DATA_ACCESS_PLAN.md`
2. **Inspect actual variable metadata** — confirm candidate variable labels against real codebooks
3. **Promote candidate variable labels to confirmed variable mappings** — update `feature_mapping_p12.yaml` with actual variable names
4. **Build first baseline_table artifacts** — compute descriptive statistics for preferred outcomes
5. **Only after baseline table validation** — consider lightweight interpretable models (logistic regression, elastic net)

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
