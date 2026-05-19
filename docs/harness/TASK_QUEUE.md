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

**Status**: done
**Goal**: Define rules for identifying structural, mutually incompatible branches from a snapshot
**Depends on**: ALT-002
**Notes**: Complete. Canonical branches.yaml, branch-discovery-workflow.md, quality gate added.

### ALT-004: Alter generation

**Status**: done
**Goal**: Generate coherent alter versions per branch with values, narrative, and tradeoffs
**Depends on**: ALT-003
**Notes**: Complete. Canonical _template.yaml, alter-generation-workflow.md, quality gate added. No active alters — branches not yet confirmed.

### ALT-005: Dialogue engine

**Status**: done
**Goal**: Facilitate dialogue between user and each Alter, injecting full alter.yaml
**Depends on**: ALT-004
**Notes**: Complete. Dialogue engine workflow defined, template created (inactive). No active sessions — no confirmed alters exist.

### ALT-006: Value alignment evaluator

**Status**: done
**Goal**: Compare Alters against user-confirmed values, not choose
**Depends on**: ALT-005
**Notes**: Complete. Value alignment workflow defined, template created (inactive). No active alignment files — no confirmed alters exist.

### ALT-007: Calibration system + rubric

**Status**: done
**Goal**: Score branches, track scores, evolve rubric (human review only)
**Depends on**: ALT-006
**Notes**: Complete. Rubric normalized with canonical structure, state.json cold_start, scores template created (inactive), calibration-system-workflow.md defined. No active scores — no checkpoints exist.

### ALT-008: Archive system

**Status**: done
**Goal**: Archive completed cycles with snapshot, branches, scores, and traces
**Depends on**: ALT-007
**Notes**: Complete. Archive template folder with 7 template files (all inactive_template_only), archive-system-workflow.md with 9 sections, quality gate added. No real archive folders created — no active cycles exist.

---

### CYCLE-001A: First real Snapshot Intake cycle

**Status**: ready-with-approval
**Goal**: Execute a real Snapshot Intake → Branch Discovery → Alter Generation → Dialogue → Value Alignment → Calibration cycle using actual user content
**Depends on**: ALT-008 (complete)
**Notes**: Ready for human approval. This is the first real cycle — requires human-provided snapshot content. Begins at Snapshot Intake (ALT-002 workflow). All templates and workflows are in place.

---

## Phase 1 — Controlled Implementation

### P1-001: Backend Foundation + Snapshot Intake Contract

**Status**: done
**Goal**: Create minimal FastAPI backend, Pydantic contracts for Snapshot Intake, and pure state-transition helpers
**Depends on**: Phase 0 complete
**Notes**: Complete. FastAPI app with /health route, Snapshot Pydantic schemas with validation, Snapshot Intake service with pure functions, 13 pytest tests passing. No frontend, no database, no LLM provider, no branch/alter/dialogue/value/calibration/archive implementations.

### P1-002: Snapshot Intake API Endpoints

**Status**: done
**Goal**: Expose Snapshot Intake workflow as REST API endpoints
**Depends on**: P1-001 (done)
**Notes**: Complete. In-memory session store, 6 API endpoints (health, create session, get session, next anchor, submit answer, confirm snapshot), 20 API tests + 13 existing tests = 33 total passing. Enforces one-question-at-a-time order. Rejects empty, duplicate, and out-of-order answers. Confirm only succeeds after all three anchors. No YAML writes, no Branch Discovery trigger.

### P1-003: Snapshot YAML Persistence / Export Gate

**Status**: done
**Goal**: Add controlled export path that serializes confirmed in-memory Snapshot into canonical Phase 0 YAML shape
**Depends on**: P1-002 (done)
**Notes**: Complete. snapshot_export.py provides snapshot_to_canonical_dict, snapshot_to_yaml, and write_snapshot_yaml. 13 new tests added (46 total passing). Confirm endpoint remains in-memory only. No YAML writes during normal confirmation. Export requires explicit target path. No frontend, no database, no LLM, no branch/alter/dialogue/value/calibration/archive code added.

### P1-004: Branch Discovery Controlled YAML Write

**Status**: done
**Goal**: Implement Branch Discovery controlled YAML write for transforming snapshot anchors into structural branches
**Depends on**: P1-003 (done)
**Notes**: Complete. Branch Discovery controlled YAML write implements three-step pipeline (tension extraction, structural branch identification, convergence). Tests validate 3-4 mutually incompatible branches from confirmed snapshot. Not a runtime backend service — controlled artifact write only.

### P1-005: Alter Generation Controlled YAML Write

**Status**: done
**Goal**: Implement Alter Generation controlled YAML write for creating Alters per confirmed branch
**Depends on**: P1-004 (done)
**Notes**: Complete. Alter Generation controlled YAML write produces coherent Alters with voice, tradeoffs, and personality drift. Tests validate Alter structure and human confirmation requirements. Not a runtime backend service — controlled artifact write only.

### P1-006: Dialogue Engine Controlled YAML Write

**Status**: done
**Goal**: Implement Dialogue Engine controlled YAML write for user-Alter dialogue sessions
**Depends on**: P1-005 (done)
**Notes**: Complete. Dialogue Engine controlled YAML write facilitates exploration between user and confirmed Alter with full alter.yaml injection. Grounding metadata present on every response. Not a runtime backend service — controlled artifact write only.

### P1-007: Value Alignment Controlled YAML Write

**Status**: done
**Goal**: Implement Value Alignment controlled YAML write for comparing Alters against user-confirmed values
**Depends on**: P1-006 (done)
**Notes**: Complete. Value Alignment evaluates four fixed dimensions (autonomy, stability, exploration, engineering_output). Comparison matrix produced. Active alignment files accepted after human confirmation (see QUALITY_GATES.md update). Not a runtime backend service — controlled artifact write only.

### P1-008: Calibration Controlled YAML Write

**Status**: done
**Goal**: Implement Calibration controlled YAML write for scoring branches against reality
**Depends on**: P1-007 (done)
**Notes**: Complete. Calibration controlled YAML write uses two-speed update model with cold-start policy. Rubric auto_modify remains false. Not a runtime backend service — controlled artifact write only.

### P1-009: Archive Controlled YAML Write

**Status**: done
**Goal**: Implement Archive controlled YAML write for preserving historical system states
**Depends on**: P1-008 (done)
**Notes**: Complete. Archive controlled YAML write preserves read-only faithful copies of current state. Rubric delta is proposal-only with reject_auto_apply. Not a runtime backend service — controlled artifact write only.

### P1-010: Flat Active Alter Schema

**Status**: done
**Goal**: Redesign Alter schema to flat active format with source_refs and quality_status fields
**Depends on**: P1-009 (done)
**Notes**: Complete. Alter schema flattened from nested structure to active flat format. Added source_refs (branch_ref, snapshot_ref) and quality_status fields. Phase 0 template marked inactive_template_only; active alters now use flat schema. See DECISION_RECORD.md Decision P1-010-01.

### P1-011: End-to-End Integration + CYCLE-001A Trigger

**Status**: blocked
**Goal**: Wire all backend services into end-to-end flow and trigger first real CYCLE-001A execution
**Depends on**: P1-010 (done), governance docs alignment
**Notes**: Blocked. Waiting for governance docs (PROJECT_BOARD, TASK_QUEUE, QUALITY_GATES, DECISION_RECORD, RISK_REGISTER) to be updated to reflect current phase state. Cannot proceed until quality gates and decision records match active artifacts.
