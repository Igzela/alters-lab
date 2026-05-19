# Alters System Lab

A personal future-branch simulation and calibration system.

## Overview

Alters System helps you explore potential future paths by modelling branching life decisions, generating alter versions of yourself for each path, and calibrating which branches best align with your values and energy.

## Core Loop

```
Intake → Branch Discovery → Alter Generation → Dialogue / Value Alignment → Calibration
```

1. **Intake** - Capture a current Snapshot: constraints, uncertainties, and what you refuse to give up
2. **Branch Discovery** - Identify structural, mutually incompatible future branches
3. **Alter Generation** - For each branch, generate an Alter: a coherent version of you living that path
4. **Dialogue / Value Alignment** - Converse with each Alter to evaluate fit, values, and tradeoffs
5. **Calibration** - Score branches against a Rubric and refine over time

## Phase 0: File-Based Workflow

Phase 0 operates entirely on local files — YAML snapshots, YAML branch definitions, YAML alters, and a JSON calibration state. No application code, no database, no LLM providers. This is the exploration and design phase before any system is built.

## Project Structure

```
alters/
  current/
    snapshot.yaml          # Current state: constraints, uncertainties, anchors
    branches.yaml          # Discovered branches with quality rules
    reality_trace.yaml     # How reality diverges from branches over time
    alters/                # Alter YAML files per branch
  calibration/
    rubric.yaml            # Evaluation dimensions (4-axis rubric)
    state.json             # Cold-start calibration state
    scores/                # Per-cycle score records
  archive/                 # Completed cycle archives
```

## License

TBD
