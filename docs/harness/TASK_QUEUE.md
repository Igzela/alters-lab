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

### P1-004: Controlled Snapshot YAML Write

**Status**: done
**Goal**: Implement Controlled Snapshot YAML Write for persisting confirmed snapshots as canonical YAML
**Depends on**: P1-003 (done)
**Notes**: Complete. Controlled Snapshot YAML Write persists confirmed snapshot as canonical YAML artifact. Not a runtime backend service — controlled artifact write only.

### P1-005: Controlled Branches YAML Write

**Status**: done
**Goal**: Implement Controlled Branches YAML Write for persisting branch discovery output as canonical YAML
**Depends on**: P1-004 (done)
**Notes**: Complete. Controlled Branches YAML Write persists branch discovery output as canonical YAML artifact. Not a runtime backend service — controlled artifact write only.

### P1-006: Controlled Alter YAML Write

**Status**: done
**Goal**: Implement Controlled Alter YAML Write for persisting alter definitions as canonical YAML
**Depends on**: P1-005 (done)
**Notes**: Complete. Controlled Alter YAML Write persists alter definitions as canonical YAML artifact. Not a runtime backend service — controlled artifact write only.

### P1-007: Value Alignment Controlled YAML Write

**Status**: done
**Goal**: Implement Value Alignment controlled YAML write for comparing Alters against user-confirmed values
**Depends on**: P1-006 (done)
**Notes**: Complete. Value Alignment evaluates five fixed dimensions (autonomy, technical_exploration, engineering_output, stability, evidence_based_decision). Comparison matrix produced. Active alignment files accepted after human confirmation (see QUALITY_GATES.md update). Not a runtime backend service — controlled artifact write only.

### P1-008: Controlled Dialogue YAML Write

**Status**: done
**Goal**: Implement Controlled Dialogue YAML Write for persisting dialogue session artifacts as canonical YAML
**Depends on**: P1-007 (done)
**Notes**: Complete. Controlled Dialogue YAML Write persists dialogue session artifacts as canonical YAML. Not a runtime backend service — controlled artifact write only.

### P1-009: Reality Trace / Weekly Evidence Controlled Write

**Status**: done
**Goal**: Implement Reality Trace / Weekly Evidence Controlled Write for persisting evidence trail as canonical YAML
**Depends on**: P1-008 (done)
**Notes**: Complete. Reality Trace / Weekly Evidence Controlled Write persists evidence trail as canonical YAML artifact. Not a runtime backend service — controlled artifact write only.

### P1-010: State Reconciliation + Active YAML Schema Normalization

**Status**: done
**Goal**: Redesign Alter schema to flat active format with source_refs and quality_status fields
**Depends on**: P1-009 (done)
**Notes**: Complete. Alter schema flattened from nested structure to active flat format. Added source_refs (branch_ref, snapshot_ref) and quality_status fields. Phase 0 template marked inactive_template_only; active alters now use flat schema. See DECISION_RECORD.md Decision P1-010-01.

### P1-011: Governance Truth Repair + Day 30 Demo Definition

**Status**: done
**Goal**: Align all governance docs with current phase state and define Day 30 demo criteria
**Depends on**: P1-010 (done)
**Notes**: Complete. Governance docs repaired to match current phase state. Day 30 demo definition documented.

### P1-012: Day 30 Evidence Harness + Schema Alignment

**Status**: done
**Goal**: Align Day 30 evidence harness with 9-step schema and regenerate evidence report
**Depends on**: P1-011 (done)
**Notes**: Complete. Harness updated to emit 9-step evidence (app_import, health_check, create_session, submit_three_anchors, confirm_snapshot_in_memory, confirm_no_yaml_write, export_to_explicit_temp_yaml, validate_active_yaml_chain, verify_no_forbidden_components). Added checks for score_*.yaml and alters/archive/20* folders. Evidence report regenerated with pass_criteria, fail_criteria_triggered, test_evidence, and overall fields.

### P1-013: Phase 1 Closeout / Day 30 Evidence Review

**Status**: blocked
**Goal**: Final review and sign-off of Day 30 evidence and Phase 1 closeout
**Depends on**: P1-012 (done)
**Notes**: Blocked. Awaiting human review of Day 30 evidence report and Phase 1 closeout decision.
