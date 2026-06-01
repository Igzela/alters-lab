# Phase 12A — Source Selection and Access Audit

## Summary

Phase 12A selects **MIDUS** and **NLSY97** as the first public baseline sources for the dual-source pilot. FFCWS and PSID are deferred.

## Source Selection Matrix

| Source | Decision | Primary Domains | Rationale |
|--------|----------|-----------------|-----------|
| NLSY97 | **include** | career_education, financial | Best longitudinal youth dataset for career/education/financial trajectories |
| MIDUS | **include** | health, relationship, subjective_wellbeing | Best psychosocial predictor coverage (personality, mastery, social support) |
| FFCWS | defer | — | High transfer risk (urban-only, non-marital oversample); defer until pilot validated |
| PSID | defer | — | Useful for wealth/family validation later; defer to avoid scope creep |

## Dataset Roles

### NLSY97 (Primary: career_education, financial)

- **What it covers**: 8,984 youth aged 12-17 in 1997, followed annually through 2019+
- **Why selected**: Annual tracking enables robust baseline tables for employment stability, degree completion, and income trajectories. Cognitive and non-cognitive assessments at baseline provide predictor variables.
- **Access**: NLS Investigator (https://www.nlsinfo.org/investigator/), free registration
- **Transfer risk**: High (US-only cohort, born 1980-1984)

### MIDUS (Primary: health, relationship, subjective_wellbeing)

- **What it covers**: ~7,000 adults aged 25-74 at baseline (1995-1996), 3 waves
- **Why selected**: Strong coverage of Big Five personality, mastery, social support, life satisfaction — directly maps to Alters Lab predictor_profile fields. Biomarker sub-study available for health outcomes.
- **Access**: ICPSR (https://www.icpsr.umich.edu/web/ICPSR/studies/04652), free registration
- **Transfer risk**: High (mid-1990s baseline, ages 25-74)

## Key Design Decisions

1. **Two-source complementarity**: NLSY97 covers career/financial trajectories; MIDUS covers health/wellbeing/relationship. Together they span all 5 Alters Lab domains.
2. **No FFCWS in pilot**: The urban-only, non-marital-oversampled design creates transfer risk that is hard to quantify. Defer until MIDUS+NLSY97 baselines are validated.
3. **PSID as future validator**: PSID's wealth data and intergenerational linkages make it valuable for later validation, not initial baseline construction.
4. **No production integration yet**: Phase 12 is inside labs/population_baseline. No outputs enter branch_forecast.

## Known Limitations

- Both datasets are US-only; generalizability to non-US populations is untested
- Both have high transfer risk to current young adults (different cohorts, different economic contexts)
- Cross-dataset harmonization is needed for shared constructs (e.g., self-rated health)
- Variable names listed in this phase are **candidate labels**, not confirmed extractions

## Config File

See `config/source_selection_v0_1.yaml` for the structured source definitions.
