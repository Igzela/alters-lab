# Next Decision Point

## Current Status (Phase 11 — Complete)

Phase 11 adds the Population Baseline Lab scaffold and public-prior integration contract. No production ML model has been added. The main forecast system remains literature-prior only for Route B.

## What Exists Now

- **Schema**: `PopulationBaselineModelCard`, `PopulationPriorArtifact`, `PublicDatasetSource`, `PublicOutcomeDefinition`, `PublicFeatureMapping` in `apps/api/src/alters_lab/schemas/population_baseline.py`
- **Contract**: `PublicPriorIntegrationContract` in `apps/api/src/alters_lab/schemas/public_prior_contract.py`
- **Lab scaffold**: `labs/population_baseline/` with example configs, model card template, data source docs
- **Validation standard**: `docs/VALIDATION_STANDARD.md` defines 6 gates
- **Positioning**: `docs/PRODUCT_POSITIONING.md` defines the public-prior + personal-calibration identity

## Next Decision: Population Baseline Lab Activation

The next meaningful decision is whether to activate the Population Baseline Lab by:

1. **Downloading a real dataset** (e.g., NLSY79 public use data)
2. **Defining real outcome measures** using the example outcome definitions as a starting point
3. **Building a baseline table or simple model** for one domain (e.g., career_education)
4. **Creating a model card** with actual calibration metrics
5. **Submitting the model card for validation gate review**

### Decision Criteria

- Is there a dataset available with a clear outcome definition?
- Can the feature mapping be validated against the existing predictor profile schema?
- Is the transfer risk manageable (i.e., can we cap confidence appropriately)?
- Does the model produce useful directional priors without false precision?

### Alternative: Literature-Only Route B

If dataset activation is too heavy, the alternative is to keep Route B literature-prior only and focus on:
- Expanding the literature prior catalog
- Improving the personal calibration pipeline
- Collecting more user evidence for Route A

## Blocked On

- User decision on whether to pursue dataset activation
- Availability of a suitable public dataset
- Time to build and validate a real model
