# Data Sources for Population Baselines

## Supported Source Candidates

### NLSY79 — National Longitudinal Survey of Youth 1979

- **Type**: Longitudinal dataset
- **Population**: 12,686 youth aged 14-22 in 1979, followed through present
- **Domains**: career_education, financial, health, relationship
- **Time horizon**: 40+ years of follow-up
- **Transfer risk**: High — US cohort, specific generation, volunteer bias
- **Access**: https://www.nlsinfo.org/
- **Notes**: Rich employment, education, income, health, family data. Extensively used in labor economics.

### NLSY97 — National Longitudinal Survey of Youth 1997

- **Type**: Longitudinal dataset
- **Population**: 8,984 youth aged 12-17 in 1997, followed through present
- **Domains**: career_education, financial, health, relationship
- **Time horizon**: 20+ years of follow-up
- **Transfer risk**: High — US cohort, younger generation, different labor market
- **Access**: https://www.nlsinfo.org/
- **Notes**: More recent than NLSY79, includes cognitive and non-cognitive assessments.

### MIDUS — Midlife in the United States

- **Type**: Longitudinal dataset
- **Population**: ~7,000 adults aged 25-74 at baseline (1995-1996)
- **Domains**: health, subjective_wellbeing, relationship
- **Time horizon**: 20+ years with biomarker sub-study
- **Transfer risk**: High — US midlife adults, volunteer sample
- **Access**: https://midus.colectica.org/
- **Notes**: Strong on psychological well-being, stress, social relationships. Biomarker data adds health rigor.

### PSID — Panel Study of Income Dynamics

- **Type**: Panel dataset
- **Population**: 18,000+ individuals tracked since 1968, intergenerational
- **Domains**: career_education, financial, health, relationship
- **Time horizon**: 50+ years, intergenerational
- **Transfer risk**: High — US families, specific sampling design
- **Access**: https://psidonline.isr.umich.edu/
- **Notes**: Longest-running household panel survey. Intergenerational linkages are unique.

### FFCWS — Future of Families and Child Wellbeing Study

- **Type**: Longitudinal dataset
- **Population**: ~5,000 children born 1998-2000, disproportionately non-marital births
- **Domains**: career_education, financial, health, relationship
- **Time horizon**: 20+ years (child follow-up to age 15+)
- **Transfer risk**: High — specific birth cohort, oversampled non-marital births
- **Access**: https://ffcws.princeton.edu/
- **Notes**: Strong on family structure, father involvement, child outcomes. Not representative of all births.

### Literature Meta-Analyses and Systematic Reviews

- **Type**: Literature review / meta-analysis
- **Domains**: All
- **Transfer risk**: Variable — depends on study quality, heterogeneity, publication bias
- **Notes**: Best used for directional priors, not exact probabilities. Examples:
  - Personality and career success (Judge et al.)
  - Conscientiousness and health outcomes (Bogg & Roberts)
  - Goal-setting and achievement (Locke & Latham)
  - Subjective well-being set-point theory (Lyubomirsky et al.)

## Transfer Risk Notes

All population datasets carry **high transfer risk** by default when applied to an individual user because:

1. **Population mismatch**: The user is not drawn from the study population
2. **Temporal mismatch**: The user lives in a different time period
3. **Cultural mismatch**: Studies are often US-centric or specific to certain cohorts
4. **Selection bias**: Volunteer participants differ from non-participants
5. **Ecological fallacy**: Population-level associations may not apply to individuals

Population priors should be treated as **directional evidence**, not individual predictions. The main Alters Lab system enforces this through the transfer_risk field and confidence caps.
