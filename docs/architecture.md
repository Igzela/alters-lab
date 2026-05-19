# Architecture Overview

## System Architecture

```
┌──────────────────────────────────────┐
│           Intake Layer               │
│  Capture snapshot, constraints,      │
│  uncertainties, anchors              │
└──────────────┬───────────────────────┘
               │
┌──────────────▼───────────────────────┐
│       Branch Discovery Engine        │
│  Identify structural, mutually       │
│  incompatible future branches        │
└──────────────┬───────────────────────┘
               │
┌──────────────▼───────────────────────┐
│        Alter Generator               │
│  Generate coherent alter versions    │
│  per branch with values & tradeoffs  │
└──────────────┬───────────────────────┘
               │
┌──────────────▼───────────────────────┐
│        Dialogue Engine               │
│  Facilitate conversation between     │
│  user and each Alter                 │
└──────────────┬───────────────────────┘
               │
┌──────────────▼───────────────────────┐
│     Value Alignment Evaluator        │
│  Evaluate branch fit against         │
│  user values and rubric              │
└──────────────┬───────────────────────┘
               │
┌──────────────▼───────────────────────┐
│       Calibration System             │
│  Score branches, track reality       │
│  traces, evolve rubric over time     │
└──────────────┬───────────────────────┘
               │
┌──────────────▼───────────────────────┐
│           Archive                    │
│  Store completed cycle results       │
└──────────────────────────────────────┘
```

## Module Breakdown

| Module | Responsibility |
|--------|---------------|
| Intake Layer | Capture current snapshot with constraints, uncertainties, and anchors |
| Branch Discovery Engine | Identify structurally distinct, mutually incompatible future branches |
| Alter Generator | Generate coherent alter versions per branch |
| Dialogue Engine | Facilitate dialogue between user and alters |
| Value Alignment Evaluator | Evaluate branch fit against user values and rubric |
| Calibration System | Score branches, track reality traces, refine rubric |
| Archive | Store completed cycle results |

## Data Flow

1. User provides current Snapshot (constraints, uncertainties, anchors)
2. Branch Discovery Engine identifies structural branches
3. Alter Generator creates Alter YAML for each branch
4. User engages in Dialogue with each Alter
5. Value Alignment Evaluator scores branches against Rubric
6. Calibration System records scores and reality traces
7. Archive stores completed cycle
8. Rubric evolves based on accumulated evidence (human review only)
