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

**Status**: done
**Goal**: Final review and sign-off of Day 30 evidence and Phase 1 closeout
**Depends on**: P1-012 (done)
**Notes**: Complete. Phase 1 sealed. Day 30 evidence report reviewed, Phase 1 closeout PASS.

---

## Phase 2 — Read-Only Runtime Foundation

### P2-001: Sealed Baseline Verification + Active YAML Loader

**Status**: done
**Goal**: Create read-only Python loaders and validation helpers for the sealed Phase 1 active YAML chain
**Depends on**: P1-013 (done/sealed baseline)
**Notes**: Complete. Loader package created (loaders/__init__.py, loaders/models.py, loaders/active_yaml.py) with read-only loading, validation, and summarization of all 9 active YAML artifacts. 11 new tests added (62 total passing). Active YAML unchanged. No forbidden runtime added.

### P2-002: Active YAML Chain Validator CLI

**Status**: done
**Goal**: Expose validate_active_yaml_chain as a CLI command for standalone validation
**Depends on**: P2-001 (done)
**Completed**: 84 tests passing, CLI returns exit 0 with PASS, JSON report generated.

### P2-003: Read-only Cycle Summary API

**Status**: done
**Goal**: Expose sealed active YAML chain summary and validation through read-only FastAPI endpoints
**Depends on**: P2-002 (done)
**Completed**: 101 tests passing, 4 read-only endpoints, no YAML modified, no forbidden routers.

### P2-004: Read-only Evidence Report API

**Status**: done
**Goal**: Expose evidence status, reports, and Day 30 demo summary through read-only FastAPI endpoints
**Depends on**: P2-003 (done)
**Completed**: 118 tests passing, 6 read-only endpoints, no YAML modified, no forbidden routers.

### P2-005: Phase 2 Closeout / Read-only Runtime Review

**Status**: done
**Goal**: Produce Phase 2 closeout report and seal read-only runtime foundation baseline
**Depends on**: P2-004 (done)
**Completed**: Closeout report produced, all boundary confirmations PASS, 118 tests passing.

---

## Phase 3 — Controlled Mutation

### P3-000: Phase 3 Scope and Boundary Plan

**Status**: done
**Goal**: Define controlled mutation boundaries before any Phase 3 implementation
**Depends on**: P2-005R (done)
**Completed**: Scope plan produced with 10 sections: executive summary, objectives, allowed writes (9 types), forbidden writes (10 items), approval gates, rollback/recovery plan, evidence requirements, final gate criteria, execution slice map (P3-001 through P3-007), risks and mitigations (R-029 through R-038). No code changes.

### P3-001: Controlled Snapshot Write API

**Status**: done
**Goal**: Implement controlled snapshot write API with governance checks and approval gates
**Depends on**: P3-000 (done)
**Completed**: Snapshot persist endpoint with approval_token validation, governance checks, audit trail. 133 tests passing.

### P3-001R: Controlled Snapshot Write API Contract Repair

**Status**: done
**Goal**: Fix contract issues identified in P3-001 review: approval_token hash-only storage, dry_run support, dependency injection for paths, strengthened schemas
**Depends on**: P3-001 (done)
**Completed**: approval_token stored as sha256 hash only in audit records, dry_run mode returns 200 without writing, dependency-injected paths for testability, strengthened request/response schemas with boundary_confirmations. 149 tests passing.
**Review note**: P3-001R failed review because: (1) magic approval token `p3-001-approved` still existed in tests, (2) persist_snapshot_to_disk still rejected non-magic tokens, (3) endpoint hardcoded target path, (4) boundary_confirmations too coarse, (5) tests used weak hash assertions.

### P3-001R2: Controlled Snapshot Write API Final Contract Repair

**Status**: done
**Goal**: Final contract repair: remove magic token, add write_snapshot_with_audit, fix path helpers, strengthen boundary confirmations, full test coverage
**Depends on**: P3-001R (done)
**Completed**: Magic approval token removed. Any non-empty token accepted as approval evidence. write_snapshot_with_audit replaces persist_snapshot_to_disk. Path helpers monkeypatchable. Boundary confirmations enumerate all forbidden mutation surfaces. 164 tests passing.
**Review note**: P3-001R2 code passed review, but stale old-schema audit evidence in phase3_write_audit.jsonl was flagged. The committed audit log contained 12 entries from accidental test writes using the old schema (action/sha256_before/sha256_after), targeting alters/current/snapshot.yaml, which falsely implied approved production writes.

### P3-001R3: Audit Evidence Cleanup

**Status**: done
**Goal**: Remove stale/unapproved old-schema audit evidence and establish audit evidence policy
**Depends on**: P3-001R2 (done)
**Completed**: Removed stale phase3_write_audit.jsonl (12 old-schema entries). Decision added: audit logs only committed for approved real persist operations. Risks R-034 through R-037 added. No code changes. No active YAML changes. 164 tests passing.

### P3-002: Controlled Branches Write API

**Status**: done
**Goal**: Implement controlled branches write API
**Depends on**: P3-001R3 (done)
**Completed**: Branches schemas (BranchDiscoveryStatus, Branch, BranchDiscoveryPayload, BranchesPersistRequest, BranchesPersistResponse), branches_persist service (branches_to_yaml, validate_branches_governance, preview_branches_persist, write_branches_with_audit), branches API router (GET /branches/health, POST /branches/persist). 17 service tests + 15 API tests. 242 tests passing. No active YAML modified.

### P3-003: Controlled Alter Write API

**Status**: done
**Goal**: Implement controlled alter write API with single and batch persist
**Depends on**: P3-002 (done)
**Completed**: Alter schemas (AlterSourceRefs, AlterQualityStatus, AlterVoice, AlterPayload, AlterPersistRequest, AlterPersistResponse, AlterBatchPersistRequest, AlterBatchPersistResponse), alters_persist service (alter_to_yaml, validate_alter_governance, validate_batch_governance, preview_alter_persist, write_alter_with_audit, write_alter_batch_with_audit), alters API router (GET /alters/health, POST /alters/persist/{alter_id}, POST /alters/persist-batch). 16 service tests + 16 API tests. 242 tests passing. No active YAML modified.

### P3-M1: Controlled YAML Write Surface Expansion

**Status**: done
**Goal**: Expand controlled write surface from snapshot-only to branches and alters using shared helpers
**Depends on**: P3-001R3 (done)
**Completed**: Shared controlled_write module (sha256_text, sha256_file, hash_approval_token, reject_blank_token, safe_backup_path, append_jsonl_audit, create_backup_if_exists). Branches write API (P3-002) and Alter write API (P3-003) implemented. main.py updated with branches_router and alters_router. 242 tests passing. No active YAML modified.

### P3-M1R: Controlled Write Surface Contract Hardening

**Status**: done
**Goal**: Harden Branches and Alters controlled write APIs so forbidden runtime/generation/calibration/archive/provider fields cannot be silently ignored or smuggled through request payloads
**Depends on**: P3-M1 (done)
**Completed**: Added `model_config = ConfigDict(extra="forbid")` to all Branches schemas (BranchDiscoveryStatus, Branch, BranchDiscoveryPayload, BranchesPersistRequest) and all Alters schemas (AlterSourceRefs, AlterQualityStatus, AlterVoice, AlterPayload, AlterPersistRequest, AlterBatchPersistRequest). Health endpoints return `mode: "controlled_write"`. Added 7 branches API smuggling tests and 10 alters API smuggling tests proving forbidden fields are rejected with 422. Added 4 branches schema defense tests and 4 alters schema defense tests documenting schema-level as first defense. Batch alter persist validates all alters before writing — filesystem failure midway is not fully transactional (risk noted). P3-M2 remains blocked.
**Review note**: P3-M1 failed review because schemas did not forbid extra fields, making forbidden-field smuggling ineffective. P3-M1R fixes the contract.

### P3-M2: Controlled Generation Draft Runtime

**Status**: done (repaired by P3-M2R)
**Goal**: Implement controlled, deterministic, draft-only generation runtime for branch and alter candidate artifacts
**Depends on**: P3-M1R (done)
**Completed**: Generation draft schemas (GenerationSourceRefs, GenerationBoundaryConfirmations, DraftGeneratorInfo, BranchDraftCandidate, AlterDraftCandidate, GenerationDraftPackage, GenerationPreviewRequest, GenerationPreviewResponse, DraftListResponse) with ConfigDict(extra="forbid"). Generation draft service (generate_draft_id, generation_boundary_confirmations, validate_generation_inputs, generate_branch_drafts_from_snapshot, generate_alter_drafts_from_branches, build_generation_draft_package, save_generation_draft_package, preview_generation_draft, list_generation_drafts). Generation draft API (GET /generation-drafts/health, POST /generation-drafts/preview, GET /generation-drafts/list). main.py updated with generation_drafts_router. .gitignore updated for alters/drafts/ and generation draft audit. 313 tests passing. No active YAML modified. No provider added. Draft-only output.
**Review note**: P3-M2 blocked because service used dict `.get()` on ActiveYamlChain dataclass, and real wrapped snapshot shape `{"snapshot": {"intake_status": {...}}}` was not handled. Tests used simplified dict fixture masking both issues. Repaired by P3-M2R.

### P3-M2R: Real Loader Integration Repair

**Status**: done
**Goal**: Fix generation draft runtime to work with real ActiveYamlChain dataclass and real wrapped YAML snapshot shape
**Depends on**: P3-M2 (done, blocked_with_notes)
**Completed**: Added normalize_active_chain (handles ActiveYamlChain dataclass, dict, None), extract_snapshot_body (wrapped/unwrapped), extract_branch_list helpers. Service type hints accept ActiveYamlChain | dict | None. API returns HTTP 500 for loader failure, HTTP 400 for validation failure. 17 new tests: normalize (4), extract (3), real wrapped shape validation (2), dataclass build (2), real loader smoke (2), error responses (2), real shape verification (1), unwrapped dict build (1). 330 tests passing. No active YAML modified.

### P3-M3: Draft Review and Promotion Boundary

**Status**: done
**Goal**: Implement controlled review boundary for generation drafts
**Depends on**: P3-M2R (done)
**Completed**: Draft review schemas (DraftReviewBoundaryConfirmations, DraftReviewDecision, DraftReviewRequest, PromotionBranchesPayload, PromotionAltersPayload, PromotionPackage, DraftReviewResponse, DraftReviewListResponse) with ConfigDict(extra="forbid"). Draft review service (draft_review_boundary_confirmations, load_draft_package, validate_draft_package_for_review, create_review_decision, build_branches_promotion_payload, build_alters_promotion_payload, build_promotion_package, save_review_decision, save_promotion_package, list_draft_reviews). Draft review API (GET /draft-review/health, POST /draft-review/{draft_id}/review, GET /draft-review/list). main.py updated with draft_review_router. 33 service tests + 16 API tests = 379 total passing. No active YAML modified. No persist API calls. No provider added. Promotion package is not active state.

### P3-M3R: Promotion Package Contract Hardening

**Status**: done
**Goal**: Harden PromotionPackage schema with guard validators to enforce invariants at schema level
**Depends on**: P3-M3 (done)
**Completed**: PromotionPackage model_validator enforces active_write_allowed must be false, requires_controlled_persist_api must be true, target_persist_apis restricted to allowed set. validate_draft_package_for_review enforces complete branch_A-D/alter_A-D, branch_ref mapping, voice.core_stance, incompatible_with non-empty. build_alters_promotion_payload validates controlled persist compatibility.

### P3-M3R2: Promotion Payload Exactness Repair

**Status**: done
**Goal**: Fix exactness validation for promotion payloads to catch duplicate IDs and incomplete sets
**Depends on**: P3-M3R (done)
**Completed**: validate_draft_package_for_review checks count==4, duplicate IDs, source_refs compatibility. build_branches/alters_promotion_payload verify exactly 4 unique items after filtering.

### P3-M4: Controlled Active Promotion Orchestration Plan

**Status**: done
**Goal**: Implement controlled orchestration planning layer that reads a reviewed promotion package and produces an execution plan for active promotion
**Depends on**: P3-M3R2 (done)
**Completed**: Promotion orchestration schemas (8 models with ConfigDict(extra="forbid"): PromotionOrchestrationBoundaryConfirmations, PromotionPlanStep, PromotionEvidenceRequirement, PromotionRollbackPlan, PromotionOrchestrationPlan, PromotionOrchestrationRequest, PromotionOrchestrationResponse, PromotionOrchestrationListResponse). Promotion orchestration service (promotion_orchestration_boundary_confirmations, validate_draft_id, load_promotion_package, validate_promotion_package_for_orchestration, build_promotion_steps, build_evidence_requirements, build_rollback_plan, build_orchestration_plan, save_orchestration_plan, list_orchestration_plans). Promotion orchestration API (GET /promotion-orchestration/health, POST /promotion-orchestration/{draft_id}/plan, GET /promotion-orchestration/list). main.py updated with promotion_orchestration_router. 437 tests passing. No active YAML modified. Plan-only layer. P3-M5 remains blocked.

### P3-M5: Controlled Promotion Execution Gate

**Status**: done
**Goal**: Implement controlled execution gate that validates whether a promotion orchestration plan is eligible for future active execution
**Depends on**: P3-M4 (done)
**Completed**: Promotion execution gate schemas (8 models with ConfigDict(extra="forbid"): PromotionExecutionGateBoundaryConfirmations, ExecutionPrerequisiteCheck, DryRunCheckResult, ExecutionPacket, PromotionExecutionGateReport, PromotionExecutionGateRequest, PromotionExecutionGateResponse, PromotionExecutionGateListResponse). Promotion execution gate service (promotion_execution_gate_boundary_confirmations, validate_draft_id, load_gate_inputs, validate_orchestration_plan_for_execution_gate, validate_promotion_package_for_execution_gate, compare_package_and_plan, build_prerequisite_checks, run_dry_run_compatibility_checks, build_execution_packet, build_gate_report, save_gate_report, list_execution_gate_reports). Promotion execution gate API (GET /promotion-execution-gate/health, POST /promotion-execution-gate/{draft_id}/check, GET /promotion-execution-gate/list). main.py updated with promotion_execution_gate_router. 502 tests passing. No active YAML modified. Gate-only layer. Live execution requires P3-M6.

### P3-M6: Controlled Promotion Live Execution

**Status**: done
**Goal**: Implement controlled live execution runtime that reads all promotion pipeline artifacts and performs safe, validated active promotion through controlled persist services
**Depends on**: P3-M5 (done)
**Completed**: Promotion live execution schemas (6 models with ConfigDict(extra="forbid"): PromotionLiveExecutionBoundaryConfirmations, LiveExecutionStepResult, PromotionLiveExecutionReport, PromotionLiveExecutionRequest, PromotionLiveExecutionResponse, PromotionLiveExecutionListResponse). Promotion live execution service (promotion_live_execution_boundary_confirmations, validate_draft_id, load_live_execution_inputs, validate_gate_for_live_execution, extract_branches_persist_payload, extract_alters_persist_payload, execute_promotion_dry_run, execute_promotion_live, build_live_execution_report, run_live_execution_gate, save_live_execution_report, list_live_execution_reports). Promotion live execution API (GET /promotion-live-execution/health, POST /promotion-live-execution/{draft_id}/run, GET /promotion-live-execution/list). main.py updated with promotion_live_execution_router. 565 tests passing. No active YAML modified. Live execution requires path_overrides and LIVE_EXECUTION_ENABLED=true. Default mode is dry_run. Token hash must match execution_packet.final_approval_token_hash.

### P3-M6R: Live Executor Persist Signature Repair

**Status**: done
**Goal**: Fix execute_promotion_live() calling controlled persist services with wrong kwargs
**Depends on**: P3-M6 (done)
**Completed**: Fixed write_branches_with_audit() call: branches_payload= -> payload=, added BranchDiscoveryPayload conversion. Fixed write_alter_batch_with_audit() call: alters_payload= -> alters=, target_dir= -> base_dir=, added AlterPayload list conversion. Fixed pre_write_hashes/post_write_hashes handling for batch alters (plural keys). Changed AlterPayload and BranchDiscoveryPayload/Status from extra="forbid" to extra="allow" to preserve full alter/branch data during re-persist. Updated 6 tests. 568 tests passing.

### P3-M7: First Human-Approved Live Promotion Run

**Status**: done
**Goal**: First controlled live promotion run using semantic no-op (re-persist current active YAML)
**Depends on**: P3-M6R (done)
**Completed**: Preflight (568 tests, clean tree). Active YAML baseline captured. Active chain validation passed. Promotion package built from current active YAML (semantic no-op). Orchestration plan, gate report, execution packet created with approval token hash. Dry-run passed. Live execution succeeded through controlled persist services. Post-live semantic comparison: all branch/alter files identical. snapshot.yaml and reality_trace.yaml unchanged. Active chain validation passed post-live. Full 568 tests pass post-live. Evidence produced: P3_M7_LIVE_PROMOTION_EVIDENCE.json. No raw tokens committed. No runtime artifacts committed.

### P3-M6R2: Raw Dict Re-persist Preserves Extras Without Weakening API Schemas

**Status**: done
**Goal**: Preserve active YAML extra fields during re-persist without weakening API smuggling boundary
**Depends on**: P3-M6R (done), P3-M7 (done)
**Completed**: Reverted AlterPayload, BranchDiscoveryPayload, BranchDiscoveryStatus to extra="forbid" (supersedes P3-M6R-01). Added validate_alter_raw_dict (dict-level required field + forbidden field validation). Added write_alter_raw_batch_with_audit (raw dict batch write via yaml.safe_dump). Added write_branches_raw_with_audit (raw dict branches write via yaml.safe_dump). Updated execute_promotion_live to use raw dict paths instead of Pydantic model path. All API smuggling boundary models remain extra="forbid". 8 new tests added. 576 tests passing. No active YAML modified. Decision P3-M6R2-01 recorded.

### P3-M8: Phase 3 Controlled Mutation Closeout Gate

**Status**: done
**Goal**: Read-only closeout gate verifying controlled mutation system is safe to seal as baseline
**Depends on**: P3-M6R2 (done), P3-M7 (done)
**Completed**: Phase 3 closeout schemas (6 models, all extra="forbid"), service with 9 verification checks (active YAML chain, evidence files, P3-M7 evidence, smuggling boundary, raw dict path, live execution safety, runtime artifacts, audit logs, governance status), API router (3 endpoints: health, report, evidence), 30 tests, governance docs updated. 606 tests passing. No active YAML modified. No live execution. No persist services called. Read-only verification only. Phase 3 sealed baseline candidate pending GPT review. P4-000 blocked.

### P3-M8R: Closeout API Read-Only Repair

**Status**: done
**Goal**: Remove file write from GET /phase3-closeout/report endpoint
**Depends on**: P3-M8 (done)
**Completed**: Removed write_phase3_closeout_artifacts import and call from API router. GET /report now builds report purely in memory. Added test proving no files created during GET /report. 606 tests passing. P4-000 ready_with_approval.

### P3-M8R2: Closeout Evidence Truth Repair

**Status**: done
**Goal**: Fix closeout evidence to distinguish tracked raw audit logs from ignored local runtime files
**Depends on**: P3-M8R (done)
**Completed**: Updated check_no_raw_audit_logs_committed to use git ls-files to check tracking status. FAIL only when audit jsonl is tracked by git. WARN when audit jsonl exists locally but is untracked/ignored. Updated check_no_runtime_artifacts_committed with same git-aware logic. Added 2 new tests (tracked audit FAIL, local audit WARN). 607 tests passing. Phase 3 closeout status: PASS_WITH_NOTES. Sealed baseline established.

### P4-000: Phase 4 Scope and Boundary Plan

**Status**: done
**Goal**: Define Phase 4 scope, boundaries, and implementation order
**Depends on**: P3-M8R2 (done)
**Completed**: Created P4_000_PHASE4_SCOPE_AND_BOUNDARY_PLAN.md. Phase 4 = Dialogue + Calibration Loop + Minimal User Workflow. 7 milestones (P4-M1 through P4-M7). Semantic mutation policy, promotion model, approval model, rollback model, audit model defined. Minimal frontend scope limited to dialogue, reality score form, calibration history. Active YAML semantic replacement blocked until explicit approval.

### P4-M1: Alter Dialogue Runtime

**Status**: done
**Goal**: Implement read-only alter dialogue runtime with full alter.yaml injection
**Depends on**: P4-000 (done), GPT/human review (done)
**Completed**: Alter dialogue schemas (7 models, all extra="forbid"), service (boundary confirmations, validate_alter_id, load_active_alter, validate_active_alter_for_dialogue, build_alter_dialogue_context, build_system_instruction, build_prompt_packet, list_active_alters, build_dialogue_response), API router (4 endpoints: health, list alters, context, prompt), main.py router registration, 49 tests. 656 tests passing. Read-only, no provider, no active YAML write, no dialogue logs persisted. provider_ready=false.

### P4-M2: Reality Score Form/API

**Status**: done
**Goal**: Implement reality score submission form/API
**Depends on**: P4-M1 (done)
**Notes**: Complete via P4-CAL-LOOP-MVP. User-submitted reality scores only. No automatic score inference.

### P4-M3: Drift Calculation

**Status**: done
**Goal**: Compute drift from supplied expected and actual scores as evidence only.
**Depends on**: P4-M2
**Notes**: Complete via P4-CAL-LOOP-MVP. No automatic regeneration.

### P4-M4: Calibration History Query

**Status**: done
**Goal**: Provide read-only access to calibration score history and derived drift evidence.
**Depends on**: P4-M3
**Notes**: Complete via P4-CAL-LOOP-MVP. History endpoint does not mutate score records.

---

### P4-M5: Rubric Delta Suggestion

**Status**: done
**Goal**: Detect repeated mismatch patterns between expected and actual scores and produce pending-review rubric suggestions only.
**Depends on**: P4-M2/P4-M3/P4-M4
**Notes**: Suggestion-only. Does not write `alters/calibration/rubric.yaml`.

### P4-M6: Archive Mechanism

**Status**: done
**Goal**: Provide explicit archive planning and copy-only checkpoint archive package creation.
**Depends on**: P4-M5
**Notes**: Archive creation is explicit-only and does not modify source files.

### P4-M7: Checkpoint Regeneration Plan

**Status**: done
**Goal**: Produce pending-review checkpoint regeneration plans from high drift evidence.
**Depends on**: P4-M6
**Notes**: Plan-only. No active YAML regeneration or branch/alter replacement.

### P4-CLOSEOUT: Phase 4 Closeout

**Status**: done
**Goal**: Verify P4-M1R through P4-M7 and produce sealed candidate evidence for the backend calibration loop.
**Depends on**: P4-M7
**Notes**: Closeout seals backend calibration scope only, not full productization.

### P5-000: Productization / Provider / Frontend Boundary Plan

**Status**: done
**Goal**: Define P5 scope as local product MVP, not hosted SaaS.
**Depends on**: P4-CLOSEOUT (done)
**Notes**: Created P5_000_PRODUCTIZATION_PROVIDER_FRONTEND_BOUNDARY_PLAN.md. P5 identity, provider modes, frontend scope, storage scope, active YAML safety, dialogue safety, persistent writes, forbidden items, exit gate, module inventory.

### P5-M1: API Product Surface Hardening

**Status**: done
**Goal**: Expose stable product-facing route inventory and health/status summary.
**Notes**: Read-only. 4 endpoints (/product/health, /routes, /status, /workflow-capabilities). No writes, no provider calls, no active YAML mutation. Route classification (safe/internal/dangerous).

### P5-M2: Provider Gateway Boundary

**Status**: done
**Goal**: All provider calls through single gateway. No feature module imports provider SDKs.
**Notes**: Default mock mode. 3 endpoints (/provider-gateway/health, /complete, /config-status). API key never returned. Secrets redacted. No active YAML modification.

### P5-M3: Provider-backed Alter Dialogue

**Status**: done
**Goal**: Provider-backed dialogue using full alter YAML prompt packet.
**Notes**: 2 endpoints (/provider-dialogue/health, /{alter_id}/reply). Mock default. No active YAML write. save_session defaults to false. Sessions written to alters/product/sessions/ only when explicitly requested.

### P5-M4: Minimal Frontend MVP

**Status**: done
**Goal**: Vite + React + TypeScript minimal UI.
**Notes**: 6 pages (SystemStatus, AlterDialogue, RealityScore, CalibrationHistory, RubricDelta, CheckpointPlan). No auth, no database. Calls only safe product APIs. No dangerous endpoint references.

### P5-M5: Durable Storage Boundary

**Status**: done
**Goal**: YAML remains default. Describe storage boundaries without adding database.
**Notes**: 2 endpoints (/storage-boundary/health, /manifest). Classifies paths: active YAML read-only, calibration score write, product session write, ignored runtime areas, evidence areas.

### P5-M6: User Workflow Integration

**Status**: done
**Goal**: Integrated workflow state and optional workflow-run record.
**Notes**: 3 endpoints (/user-workflow/health, /state, /run-summary). No provider calls in state. Run summary writes to alters/product/workflow_runs/ only.

### P5-M7: Safety Review and Product Closeout

**Status**: done
**Goal**: Verify productization boundaries, not production readiness.
**Notes**: 3 read-only endpoints (/phase5-closeout/health, /report, /evidence). 9 verification checks. Generates PHASE5_CLOSEOUT_EVIDENCE.json and P5_FINAL_EVIDENCE.json.

### P5-M8: Local Release Candidate

**Status**: done
**Goal**: Document local workflow demo steps and safety notes.
**Notes**: Created P5_LOCAL_RELEASE_CANDIDATE.md with backend/frontend start commands, provider explanation, demo steps, safety notes, route inventory.

### P5-CLOSEOUT: Phase 5 Closeout

**Status**: done
**Goal**: Final verification of P5 productization boundary.
**Notes**: 802 tests passing. 17 new API routes. No active YAML modified. No secrets committed. No database migration. P6-000 blocked pending GPT/human review.

### P6-000: Personal Long-Term Use Hardening Plan

**Status**: done
**Goal**: Create P6 plan and decision ledger from completed grill session. P6 is personal long-term use hardening, not public productization.
**Depends on**: P5-CLOSEOUT (done)
**Notes**: P6 identity defined. 30 core decisions recorded. 11 milestones (P6-M1 through P6-M11) planned. P6 success = behavior change after 4-week validation. P6-M1 ready_with_approval. P7-000 blocked.

### P6-CODE-COMPLETE: P6 Runtime Code Complete

**Status**: accepted
**Goal**: Merge P6-M1 through P6-M11 runtime code as code complete only.
**Depends on**: P6-000 (done)
**Notes**: Accepted and merged to main at cdf4d4e6bf20c3ed160c429c1520dd1ec74917e1. This is not behavior validation and not a sealed P6 baseline.

### P6-ENDGAME: Real-Use Validation Orchestration

**Status**: running
**Goal**: Orchestrate Week 1-4 real-use evidence collection, behavior validation, and final closeout without fabricating evidence.
**Depends on**: P6-CODE-COMPLETE (accepted)
**Allowed outputs now**: runbook, weekly note template, validation checklist, operator guide, helper scripts, governance updates.
**Runtime writes**: Only allowed when Charlie provides real weekly note content. Runtime records remain gitignored and must not be committed raw.
**Current blocker**: Week 1 raw Obsidian weekly note has not been provided.
**Current state**: CODE_COMPLETE, P6_BLOCKED_BY_REAL_USE_WINDOW, NOT_SEALED.

#### P6-ENDGAME Week 1-4 Execution Checklist

- [ ] Week 1: Charlie provides real raw Obsidian weekly note.
- [ ] Week 1: Ingest note, complete weekly review, create calibration record, complete/skip reminder.
- [ ] Week 2: Repeat after one real week; do not backdate.
- [ ] Week 3: Repeat after one real week; do not backdate.
- [ ] Week 4: Repeat after one real week; do not backdate.
- [ ] Pattern review: Run only after 4 real weekly review records exist.
- [ ] Evidence check: Confirm 4 weekly reviews, 4 calibration records, 1 pattern review, and 21-day minimum window.
- [ ] Behavior validation: Run only after evidence check passes.
- [ ] Phase6 closeout: Run only after behavior validation returns P6_BEHAVIOR_VALIDATED.

### P6-M1: Obsidian Weekly Note Ingest

**Status**: code_complete_accepted
**Goal**: Parse semi-fixed weekly note, preserve raw note, produce editable extracted record.
**Depends on**: P6-000 (done)
**Notes**: Implemented with schema/service/API/tests. Raw note is preserved, extracted records mark derived_from_raw_note, edits require correction_note and produce diff/challenge metadata.

### P6-M2: Weekly Review Session Runtime

**Status**: code_complete_accepted
**Goal**: Structured prefill -> alter recommendation -> dialogue -> review_note + calibration_record.
**Depends on**: P6-M1 (code_complete_pending_review)
**Notes**: Implemented runtime session container derived from ingested weekly note. Completion creates review note and calibration shell without auto-scoring.

### P6-M3: Action Alignment Scoring

**Status**: code_complete_accepted
**Goal**: Implement direction_alignment, execution_consistency, avoidance_level, evidence requirements, and next correction rule.
**Depends on**: P6-M2
**Notes**: Implemented explicit score records with required action/friction/correction evidence. No provider truth, active YAML write, or rubric mutation.

### P6-M4: Self-Deception and Challenge Layer

**Status**: code_complete_accepted
**Goal**: Implement self_deception_risk, rationalization_pattern, evidence-based challenge, edit challenge.
**Depends on**: P6-M3
**Notes**: Implemented medium/high risk field requirements, strong challenge gate, and edit challenge triggers for softening edits.

### P6-M5: Alter Recommendation Engine

**Status**: code_complete_accepted
**Goal**: Recommend primary alter and optional counter-alter using defined factors.
**Depends on**: P6-M2
**Notes**: Implemented deterministic factor scoring, optional counter-alter triggers, and override-with-reason flow.

### P6-M6: Reminder / Skip-with-Reason Flow

**Status**: code_complete_accepted
**Goal**: Weekly reminder state and skip reason record.
**Depends on**: P6-M2
**Notes**: Implemented fixed reminder status, skip-with-reason, complete, and history records. Skips count toward usage integrity.

### P6-M7: 4-Week Pattern Review

**Status**: code_complete_accepted
**Goal**: Detect repeated patterns and impose strategy constraints when threshold met.
**Depends on**: P6-M3
**Notes**: Implemented 4-week pattern detection with 3/4 high-confidence threshold and strategy constraint output.

### P6-M8: Data Retention / Export / Delete

**Status**: code_complete_accepted
**Goal**: Manual delete, export, archive controls for weekly review records.
**Depends on**: P6-M2
**Notes**: Implemented manifest/export/delete/archive controls for P6 runtime areas only. Export/archive output is sanitized and active YAML is untouched.

### P6-M9: Real Provider Optional Enablement

**Status**: code_complete_accepted
**Goal**: Provider remains disabled/mock by default. Explicit configuration only. No auto-mutation.
**Depends on**: P6-M2
**Notes**: Implemented P6 provider policy status and explicit config validation. No new provider stack or direct SDK imports.

### P6-M10: Behavior Validation Gate

**Status**: implemented_waiting_real_use
**Goal**: After 4 weeks, judge P6 as P6_BEHAVIOR_VALIDATED, P6_FAILED_TO_VALIDATE, or P6_USAGE_INVALID.
**Depends on**: P6-M1 through P6-M9
**Notes**: Implemented gate logic. R1 repair verifies persisted weekly review/calibration/pattern records, rejects fake or missing IDs, and requires a real 4-week window. It returns P6_INSUFFICIENT_DATA until real use provides verified evidence.

### P6-M11: P6 Closeout

**Status**: implemented_blocked_by_behavior_validation
**Goal**: Only seal P6 if behavior validation passes.
**Depends on**: P6-M10
**Notes**: Implemented read-only closeout report/evidence endpoints. R1 repair re-verifies latest validation against persisted evidence. Closeout remains BLOCKED unless latest behavior validation is P6_BEHAVIOR_VALIDATED and evidence re-verifies.

### P6-BEHAVIOR-VALIDATION: Real 4-Week Behavior Validation

**Status**: blocked_by_real_use_window
**Goal**: Produce P6_BEHAVIOR_VALIDATED only from verified persisted evidence.
**Depends on**: P6-ENDGAME Week 1-4 evidence complete
**Notes**: Requires 4 weekly reviews, 4 calibration records, 1 pattern review, and a real 4-week evidence window. Fake IDs, manual validation records, and short windows must remain blocked.

### P6-CLOSEOUT: Final Phase 6 Closeout

**Status**: blocked
**Goal**: Seal P6 only after behavior validation passes and phase6 closeout returns PASS.
**Depends on**: P6-BEHAVIOR-VALIDATION
**Notes**: Current expected closeout status is BLOCKED. Do not mark P6 sealed before verified behavior validation.

### P7-000: Local App Distribution Boundary Plan

**Status**: done
**Goal**: Define P7 as local app distribution for Linux/Debian-style systems without replacing P6 behavior validation.
**Depends on**: P6 runtime CODE_COMPLETE; P6 behavior validation still blocked by real-use window
**Notes**: Created P7 boundary plan, taskbook, runtime layout, and packaging boundary. P7 enables P6 real use without coding tools, but does not validate or seal P6. No runtime code, frontend code, packaging scripts, active YAML, rubric, provider config code, deb package, or raw runtime records changed.

### P7-M1: Runtime Layout Externalization

**Status**: done
**Goal**: Refactor path handling so packaged mode writes runtime data to user data directories while dev mode remains repo-compatible.
**Depends on**: P7-000 (done)
**Notes**: Runtime layout resolver added with dev and packaged modes. P6 runtime helper preserves explicit repo_root/tmp_path behavior and can write packaged runtime records under user data/product paths. Added `/runtime-layout/health`, `/runtime-layout/status`, and `/runtime-layout/ensure-config`. Active YAML/rubric protections remain false. No `.deb`, launcher, provider UI, real provider calls, P6 validation, or P6 sealing.

### P7-M2: Unified Local Server

**Status**: done
**Goal**: Serve built frontend from FastAPI and add local app health/status endpoints.
**Depends on**: P7-M1
**Notes**: Added unified local server layer. FastAPI now exposes `/local-app/health`, `/local-app/status`, and `/local-app/frontend-status`; serves built frontend index at `/`; serves `/assets/*` from frontend dist only; and provides SPA fallback without shadowing known API prefixes. Missing dist returns a clear placeholder without crashing API. Frontend build verified. No `.deb`, launcher, provider UI, provider calls, P6 validation, or P6 seal.

### P7-M3: CLI Launcher

**Status**: ready_with_approval
**Goal**: Add `alters-lab start`, `stop`, `status`, `open`, and `doctor`.
**Depends on**: P7-M2
**Notes**: Next recommended action. Must start one local backend/UI server, open browser, handle port conflicts, and write logs under `~/.local/state/alters-lab/logs`.

### P7-M4: Provider Configuration UI/API

**Status**: blocked
**Goal**: Add local provider settings page/API with disabled/mock/openai-compatible-http modes and secret redaction.
**Depends on**: P7-M3
**Notes**: Blocked until launcher/status surface exists.

### P7-M5: Debian Package Build

**Status**: blocked
**Goal**: Create packaging scaffold and build `.deb` installing app code to `/opt/alters-lab`.
**Depends on**: P7-M4
**Notes**: Blocked until local app startup and provider config boundaries are stable.

### P7-M6: Desktop Integration

**Status**: blocked
**Goal**: Add desktop launcher and optional icon.
**Depends on**: P7-M5
**Notes**: Blocked until package-owned paths and launcher are available.

### P7-M7: Upgrade / Uninstall / Data Safety

**Status**: blocked
**Goal**: Define and implement upgrade/uninstall behavior and backup/export command.
**Depends on**: P7-M6
**Notes**: Blocked until package install behavior exists.

### P7-M8: Local App Release Candidate

**Status**: blocked
**Goal**: Run full local app smoke test from deb install through weekly review flow and runtime record storage.
**Depends on**: P7-M7
**Notes**: Must confirm active YAML/rubric unchanged and P6 remains not validated/not sealed.

### P7-M9: P7 Closeout

**Status**: blocked
**Goal**: Verify local app release candidate and keep P8 blocked.
**Depends on**: P7-M8
**Notes**: Must not claim P6 behavior validation or start P8.
