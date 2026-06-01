# Phase 12C — Feature Mapping Refinement

## Summary

Maps **15 constructs** from MIDUS and NLSY97 to internal Alters Lab predictor_profile fields and behavior_metric IDs. All variable names are **candidate labels** pending actual dataset metadata inspection.

## Mapping Count by Source

| Source | Features | Preferred | Candidate |
|--------|----------|-----------|-----------|
| MIDUS | 12 | 7 | 5 |
| NLSY97 | 3 | 2 | 1 |
| **Total** | **15** | **9** | **6** |

## Mapping Architecture

```
Public Dataset Variables (MIDUS / NLSY97)
        │
        ▼  [candidate_variable_labels → confirmed after inspection]
Alters Lab Predictor Profile Fields
        │
        ▼  [behavior metrics tracked separately]
Behavior Metric IDs
```

## Key Construct Mappings

### Personality → trait_baseline
| Construct | Source | Maps To |
|-----------|--------|---------|
| Conscientiousness | MIDUS B1SCON | trait_baseline.conscientiousness |
| Neuroticism | MIDUS B1SNEU | trait_baseline.neuroticism_negative_emotionality |
| Extraversion | MIDUS B1SEXT | trait_baseline.extraversion |
| Agreeableness | MIDUS B1SAGR | trait_baseline.agreeableness |
| Openness | MIDUS B1SOPN | trait_baseline.openness |

### Life context → current_context
| Construct | Source | Maps To |
|-----------|--------|---------|
| Educational attainment | NLSY97 CV_HGC | current_context.education_status |
| Employment status | NLSY97 CV_WKSTAT | current_context.employment_status |
| Financial stability | NLSY97 CV_INCOME_GROSS | current_context.financial_stability |
| Relationship status | MIDUS B1SMSTAT | current_context.relationship_status |
| Health constraints | MIDUS B1SA1 | current_context.health_constraints |
| Social support | MIDUS B1SCALL | current_context.social_support |

### Behaviors → behavior_metric_ids
| Construct | Source | Maps To |
|-----------|--------|---------|
| Mastery | MIDUS B1SCMAS | key_milestone_progress |
| Sleep regularity | MIDUS B1SA52A/B | sleep_regular_nights |
| Physical activity | MIDUS B1SA40A/B | moderate_vigorous_activity_minutes |

## Important Caveats

1. **Variable names are candidates**: All `source_variable_candidates` entries need verification against actual MIDUS/NLSY97 codebooks. Do not treat as final.
2. **MIDUS dominates personality mapping**: NLSY97 has no direct Big Five measure; locus of control is a weak proxy.
3. **NLSY97 dominates career/financial**: Longitudinal income and employment data is NLSY97's strength.
4. **Cross-harmonization needed**: Self-rated health appears in both datasets but with different item structures. Harmonization is deferred.
5. **No behavior_metrics directly extractable**: Public datasets measure traits and contexts, not daily behavioral tracking. Behavior metric mappings are conceptual bridges, not direct extractions.

## Config File

See `config/feature_mapping_p12.yaml` for structured definitions.
