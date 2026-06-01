# Phase 12B — Outcome Definition Refinement

## Summary

Defines **17 candidate outcomes** across 5 domains for the MIDUS + NLSY97 dual-source pilot. All outcomes are candidates pending variable metadata inspection from actual datasets.

## Outcome Count by Domain

| Domain | Source | Outcomes | Preferred | Candidate |
|--------|--------|----------|-----------|-----------|
| career_education | NLSY97 | 4 | 1 | 3 |
| financial | NLSY97 | 2 | 1 | 1 |
| health | MIDUS | 3 | 1 | 2 |
| relationship | MIDUS | 3 | 1 | 2 |
| subjective_wellbeing | MIDUS | 5 | 3 | 2 |
| **Total** | | **17** | **7** | **10** |

## Design Principles

1. **Domain alignment**: Each outcome maps to one of the 5 Alters Lab branch domains
2. **Source specialization**: NLSY97 for career/financial trajectories; MIDUS for health/wellbeing/relationship
3. **Measurement types**: Mix of binary, ordinal, and continuous outcomes to avoid overfitting to easy binary splits
4. **Direction encoding**: Each outcome has explicit `target_direction` (higher_is_better, lower_is_better, category_dependent)
5. **Missingness risk**: Flagged per outcome to guide later data cleaning priorities
6. **Transfer risk**: Rated per outcome, not just per dataset

## Preferred vs Candidate Status

- **preferred** (7): Outcomes with clear operational definitions, low missingness risk, and direct mapping to Alters Lab domains
- **candidate** (10): Outcomes that are conceptually relevant but may have measurement challenges, higher missingness, or weaker mapping

## Key Decisions

### No life_score or exact personal probabilities
None of these outcomes produce a "life score" or exact probability. They are population-level baselines for directional reference only.

### No survival analysis in first pass
While some outcomes have natural time-to-event structure (e.g., employment stability), the first pass uses simpler binary/ordinal definitions. Survival models can be added later.

### Cross-harmonization deferred
Some constructs (e.g., self-rated health) appear in both MIDUS and NLSY97 but with different variable structures. Cross-dataset harmonization is deferred to Phase 12C feature mapping.

## Config File

See `config/outcome_definitions_p12.yaml` for structured definitions.
