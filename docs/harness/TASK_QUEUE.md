# Task Queue

## Execution Slices

### COC-001: Repo skeleton + governance docs

**Status**: done
**Goal**: Initialize repository structure and governance documentation
**Notes**: Complete. Repo skeleton created.

### COC-002: Backend schema definitions (Pydantic models)

**Status**: paused
**Goal**: Define Pydantic v2 models for all domain entities
**Depends on**: COC-001
**Notes**: PAUSED. Content calibration direction has been replaced by Alters System. This task is retired.

### COC-003 through COC-008

**Status**: retired
**Notes**: All content calibration tasks after COC-002 are retired. See ALT-* tasks for new direction.

---

### ALT-001: Reset project direction to Alters System + Phase 0 workspace

**Status**: done
**Goal**: Replace content-calibration direction with Alters System. Create file-based Phase 0 workspace.
**Allowed files**: README.md, AGENTS.md, docs/**, alters/**
**Forbidden**: apps/**, packages/**, .env, pyproject.toml, package.json, any business code, any frontend/backend code

### ALT-002: Snapshot intake workflow

**Status**: done
**Goal**: Define and implement snapshot capture process: constraints, uncertainties, anchors
**Depends on**: ALT-001
**Notes**: Complete. Canonical snapshot.yaml, intake-workflow.md, quality gate added.

### ALT-003: Branch discovery engine

**Status**: running
**Goal**: Define rules for identifying structural, mutually incompatible branches from a snapshot
**Depends on**: ALT-002

### ALT-004: Alter generation

**Status**: blocked
**Goal**: Generate coherent alter versions per branch with values, narrative, and tradeoffs
**Depends on**: ALT-003

### ALT-005: Dialogue engine

**Status**: todo
**Goal**: Facilitate dialogue between user and each Alter, injecting full alter.yaml
**Depends on**: ALT-004

### ALT-006: Value alignment evaluator

**Status**: todo
**Goal**: Evaluate branch fit against user values and rubric dimensions
**Depends on**: ALT-005

### ALT-007: Calibration system + rubric

**Status**: todo
**Goal**: Score branches, track scores, evolve rubric (human review only)
**Depends on**: ALT-006

### ALT-008: Archive system

**Status**: todo
**Goal**: Archive completed cycles with snapshot, branches, scores, and traces
**Depends on**: ALT-007
