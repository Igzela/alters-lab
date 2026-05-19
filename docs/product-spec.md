# Product Specification

## Alters System — Personal Future-Branch Simulation and Calibration

### 1. System Definition

Alters System is a personal tool for exploring potential future life paths. It takes a snapshot of your current state, discovers structural branching decisions, generates coherent alter versions of yourself for each path, facilitates dialogue between you and those alters, and calibrates which branches best match your values.

### 2. Core Goals

- Help you identify and articulate the structural branches in your life
- Generate plausible alter versions that embody each path
- Create a space for dialogue between you and your possible futures
- Calibrate your decision-making against a personal rubric
- Track how reality diverges from predicted branches over time

### 3. Core Concepts

#### 3.1 Snapshot

A structured capture of your current life state: heaviest constraint, most unclear direction, and what you are unwilling to give up. The anchor points for all branch generation.

#### 3.2 Branch

A structurally distinct, mutually incompatible future path. Branches differ in kind, not degree — they represent fundamentally different directions, not gradations of the same path.

#### 3.3 Alter

A coherent version of you living a specific branch. Each Alter has values, tradeoffs, and a narrative consistent with that path. Alters are generated per branch.

#### 3.4 Reality Trace

A record of how actual life diverges from predicted branches over time. Used to evaluate calibration accuracy.

#### 3.5 Rubric

A 4-axis evaluation framework: execution discipline, exploration freedom, life state match, and energy level. Used to score branches and Alters. Rubric cannot auto-modify.

### 4. Non-Goals (v0.1)

- No application code (Phase 0 is file-based)
- No database persistence
- No LLM provider integration
- No multi-user support
- No content creation or publishing features
- No API layer

### 5. User Stories

- As a user, I want to capture my current state so I have clear anchor points
- As a user, I want to discover structural branches so I can see my real options
- As a user, I want to generate Alters so I can embody each path
- As a user, I want to dialogue with my Alters so I can evaluate tradeoffs
- As a user, I want to score branches against a rubric so I can make informed decisions
- As a user, I want to track reality traces so I can calibrate over time

### 6. Constraints (v0.1)

- Single user
- File-based storage only (YAML + JSON)
- No real LLM integration
- No external API calls
- No application code
