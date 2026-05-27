# Decision Record

## Template

### Decision [ID]

**Date**: YYYY-MM-DD
**Status**: proposed | accepted | rejected | superseded
**Context**: What situation necessitated this decision?
**Decision**: What was decided?
**Consequences**: What are the trade-offs?
**Alternatives**: What other options were considered?

## Decisions

### Decision ALT-002-01: Phase 0 intake remains file-based

**Date**: 2026-05-19
**Status**: accepted
**Context**: ALT-002 implements the snapshot intake workflow. The question was whether to introduce any application code for intake or keep it file-based.
**Decision**: Phase 0 intake remains entirely file-based. No backend, frontend, database, or LLM provider code. The intake workflow is a manual process documented in intake-workflow.md, with snapshot.yaml as the sole output artifact.
**Consequences**: Intake is slower and requires manual effort, but keeps Phase 0 scope minimal and avoids premature complexity. The workflow can be automated in later phases once the file-based process is validated.
**Alternatives**: Build a CLI intake tool (deferred to later phases). Build a web intake form (deferred to later phases).

### Decision ALT-003-01: Branch discovery uses three-step pipeline

**Date**: 2026-05-19
**Status**: accepted
**Context**: ALT-003 defines how snapshot anchors are transformed into structural branches. The question was how to structure the transformation process.
**Decision**: Branch Discovery uses a three-step pipeline: (1) Tension Extraction — identify irreducible tensions from snapshot anchors, (2) Structural Branch Identification — generate candidate branches that represent active structural choices, (3) Convergence — reduce to 3-4 mutually incompatible branches. The pipeline is documented, not automated.
**Consequences**: The three-step structure provides clear traceability from snapshot to branches. Each step has defined inputs and outputs, making it auditable. The convergence step enforces quality by filtering out result-only and parameter-only differences.
**Alternatives**: Single-step branch generation (rejected — too opaque, hard to audit). Two-step pipeline (rejected — tension extraction and structural identification are distinct cognitive operations).

### Decision ALT-003-02: Branch template includes invalid_if field

**Date**: 2026-05-19
**Status**: accepted
**Context**: ALT-003 defines the canonical branch structure. The question was whether branches should include pre-defined conditions that would invalidate them.
**Decision**: Each branch includes an `invalid_if` field — a list of observable conditions that would prove the branch wrong within 30 days. This enables the Calibration system (ALT-007) to score branches against reality.
**Consequences**: Branches are falsifiable from the start. This prevents wishful thinking and ensures branches can be evaluated against real outcomes. The invalid_if field must be filled with concrete, observable conditions, not vague hopes.
**Alternatives**: Omit invalid_if (deferred to Calibration phase) — rejected because making branches falsible upfront improves branch quality and prevents unfalsifiable branches.

### Decision ALT-004-01: Alter template is inactive in Phase 0

**Date**: 2026-05-19
**Status**: accepted
**Context**: ALT-004 defines the Alter Generation workflow. The question was whether to generate active alters or keep the template inactive until branches are confirmed.
**Decision**: The `_template.yaml` is marked `inactive_template_only`. No active `alter_*.yaml` files are generated in Phase 0. The template defines the exact structure for future generation, but generation requires human-confirmed branches — which do not yet exist.
**Consequences**: Phase 0 remains documentation-only. The template provides a clear target structure without premature generation. Active generation is deferred until snapshot intake and branch discovery are completed and confirmed by a human.
**Alternatives**: Generate placeholder alters (rejected — violates no-invention rule, creates false artifacts).

### Decision ALT-004-02: Intake status canonical name is "completed"

**Date**: 2026-05-19
**Status**: accepted
**Context**: ALT-003's branch-discovery-workflow.md referenced `intake_status: "completed"` but the canonical snapshot.yaml uses `intake_status.phase: "completed"`. The naming was inconsistent.
**Decision**: Fixed branch-discovery-workflow.md to use `intake_status.phase: "completed"` matching the canonical snapshot structure. The phase field is the correct accessor.
**Consequences**: All docs now reference the same canonical field path. Future workflows can reliably check `intake_status.phase` without ambiguity.
**Alternatives**: Change snapshot.yaml to use `intake_status: "completed"` (rejected — the nested structure is more extensible and already established).

### Decision ALT-005-01: Dialogue template is inactive in Phase 0

**Date**: 2026-05-19
**Status**: accepted
**Context**: ALT-005 defines the Dialogue Engine workflow. The question was whether to create active dialogue sessions or keep the template inactive until alters are confirmed.
**Decision**: The `_template.yaml` is marked `inactive_template_only`. No active `dialogue_*.yaml` or `session_*.yaml` files are created in Phase 0. The template defines the exact structure for future sessions, but sessions require human-confirmed alters — which do not yet exist.
**Consequences**: Phase 0 remains documentation-only. The template provides a clear target structure without premature session creation. Active dialogue is deferred until snapshot intake, branch discovery, and alter generation are completed and confirmed by a human.
**Alternatives**: Create example dialogue sessions with placeholder data (rejected — violates no-invention rule, creates false artifacts).

### Decision ALT-006-01: Value Alignment template is inactive in Phase 0

**Date**: 2026-05-19
**Status**: accepted
**Context**: ALT-006 defines the Value Alignment Evaluator workflow. The question was whether to create active alignment files or keep the template inactive until alters are confirmed.
**Decision**: The `_template.yaml` is marked `inactive_template_only`. No active `alignment_*.yaml` files are created in Phase 0. The template defines the exact structure for future evaluation, but evaluation requires user-confirmed values and active alters — which do not yet exist.
**Consequences**: Phase 0 remains documentation-only. The template provides a clear target structure without premature alignment scoring. Active evaluation is deferred until snapshot, branches, alters, and user values are confirmed.
**Alternatives**: Create placeholder alignment files with invented values (rejected — violates no-invention rule, no-auto-choice rule).

### Decision ALT-006-02: Value alignment uses five fixed dimensions

**Date**: 2026-05-19
**Status**: accepted
**Context**: ALT-006 defines the alignment dimensions used to compare Alters. The question was which dimensions to use and whether they should be configurable.
**Decision**: Five fixed dimensions for Phase 0: autonomy, stability, exploration, engineering_output, relationship_life. These cannot be modified, weighted, or extended automatically. Changes require explicit human review and a decision record.
**Consequences**: Fixed dimensions provide consistency across evaluations and prevent dimension gaming. The constraint forces honest assessment against a stable framework. Extensibility is deferred to later phases with human approval.
**Alternatives**: Configurable dimensions (rejected — too early, invites gaming). Fewer dimensions (rejected — misses key life areas). More dimensions (rejected — adds complexity without benefit in Phase 0).

### Decision ALT-007-01: Calibration uses two-speed update model

**Date**: 2026-05-19
**Status**: accepted
**Context**: ALT-007 defines the Calibration System. The question was how frequently calibration should run and what triggers deeper review.
**Decision**: Two-speed model: lightweight two-week check-ins (record actuals, compute drift) plus full checkpoint regeneration on trigger (drift threshold, new constraints, user request). This balances effort with responsiveness.
**Consequences**: Frequent lightweight check-ins provide continuous data without overwhelming the user. Checkpoint regeneration is reserved for significant drift events, preventing rubric churn.
**Alternatives**: Single-speed (weekly full scoring — rejected, too burdensome). Single-speed (monthly — rejected, too slow to catch drift). Event-driven only (rejected, no regular cadence).

### Decision ALT-007-02: Cold-start policy defers scoring for first 3 checkpoints

**Date**: 2026-05-19
**Status**: accepted
**Context**: ALT-007 defines when calibration scoring begins. The question was whether to score immediately or establish a baseline first.
**Decision**: Cold-start policy: first 3 check-ins record actual values only (no drift computation, no score files). This establishes a baseline before comparison begins. Scoring starts after baseline exists.
**Consequences**: Prevents premature drift calculations against uninformed predictions. The baseline ensures first real scores are grounded in observed reality, not assumptions.
**Alternatives**: Score from first check-in (rejected — no baseline, predictions may be uninformed). Skip cold-start (rejected — no safeguard against uninformed predictions).

### Decision ALT-007-03: Rubric evolution requires human confirmation

**Date**: 2026-05-19
**Status**: accepted
**Context**: ALT-007 defines when and how the rubric can change. The question was whether drift observations can automatically modify the rubric.
**Decision**: Rubric evolution requires explicit human review and confirmation. `auto_modify: false` is permanent. Drift observations inform but do not trigger rubric changes. All changes documented in decision records.
**Consequences**: Prevents rubric gaming and ensures stability. The rubric remains a trusted reference point that only changes through deliberate human decisions.
**Alternatives**: Auto-modify on high drift (rejected — invites gaming, destabilises rubric). Auto-modify with human override (rejected — still allows automatic changes, undermines trust).

### Decision ALT-008-01: Archive is read-only faithful copy

**Date**: 2026-05-19
**Status**: accepted
**Context**: ALT-008 defines the Archive System. The question was whether archives could modify state or were purely read-only snapshots.
**Decision**: Archives are read-only faithful copies of current state. Once created, no archive content may be modified. Every file in the archive must match the current state at archive time with no invented or assumed fields.
**Consequences**: Archives are reliable historical records. They can be trusted for comparison, learning, and audit. The constraint prevents drift or revisionism in archived data.
**Alternatives**: Allow post-archival annotation (rejected — introduces revisionism risk). Allow archive updates (rejected — undermines archival integrity).

### Decision ALT-008-02: No real archives in Phase 0

**Date**: 2026-05-19
**Status**: accepted
**Context**: ALT-008 implements the Archive System workflow. The question was whether to create example archive folders.
**Decision**: No real dated archive folders (e.g., `alters/archive/2026-05-19_*`) are created in Phase 0. Only the `_template` folder exists. Real archives require active cycles with confirmed snapshot, branches, and resolution — none of which exist yet.
**Consequences**: Phase 0 remains documentation-only. The template provides the target structure without creating false artifacts. Real archives are deferred until the system has active cycles.
**Alternatives**: Create example archive with placeholder data (rejected — violates no-invention rule, creates false artifacts).

### Decision P0-CLOSEOUT-01: Phase 0 workspace complete, ready for first real Snapshot Intake

**Date**: 2026-05-19
**Status**: accepted
**Context**: P0-CLOSEOUT-001 performed the final gate review of the Phase 0 workspace. All 5 checks passed: 7 workflow docs exist, 10 workspace templates exist, no forbidden active artifacts found, quality gates exist for all 7 systems, and ALT-001 through ALT-008 are all complete.
**Decision**: Phase 0 workspace is complete. The first real cycle (CYCLE-001A) is ready-with-approval. CYCLE-001A begins with a real Snapshot Intake using human-provided content, following the intake-workflow.md process.
**Consequences**: The system has all templates, workflows, and quality gates needed to execute a real cycle. No further Phase 0 scaffolding is needed. The next action requires human initiative to provide snapshot content.
**Alternatives**: Defer to a later date (no action needed — workspace is stable and ready).

### Decision ALT-008-03: Rubric delta within archive is proposal-only with reject_auto_apply

**Date**: 2026-05-19
**Status**: accepted
**Context**: ALT-008 defines how rubric changes interact with the archive. The question was whether archived rubric deltas should auto-apply.
**Decision**: Rubric deltas within archives are proposal-only. `reject_auto_apply: true` is permanent. The proposal sits inactive until human explicitly confirms it. Every rubric change requires a linked decision record.
**Consequences**: Prevents rubric drift through archive accumulation. The archive system cannot modify the rubric — it can only propose changes that require human approval. This preserves rubric stability.
**Alternatives**: Allow archive-triggered rubric updates (rejected — undermines rubric stability, enables gaming through strategic archiving).

### Decision P1-001-01: Phase 1 starts with Snapshot Intake backend contract before Branch/Alter automation

**Date**: 2026-05-19
**Status**: accepted
**Context**: Phase 1 begins Controlled Implementation. The question was whether to start with backend contracts for Snapshot Intake or jump to full-stack Branch/Alter automation.
**Decision**: Phase 1 starts with Snapshot Intake backend contract (P1-001). Snapshot is the root artifact — Branch Discovery and Alter Generation must not be automated until Snapshot contract and validation are stable.
**Consequences**: The backend foundation is minimal and testable. Next slices can add API endpoints and then Branch/Alter automation on a stable base. Prevents premature complexity and ensures validation rules are locked down before downstream systems depend on them.
**Alternatives**: Start with Branch/Alter generation (rejected — premature, no stable contract). Start with full-stack implementation (rejected — too many moving parts, risk of premature provider integration).

### Decision P1-002-01: P1-002 exposes Snapshot Intake through in-memory API before file persistence

**Date**: 2026-05-19
**Status**: accepted
**Context**: P1-002 needed to expose the Snapshot Intake state machine through FastAPI endpoints. The question was whether to implement file persistence (YAML writes) alongside the API or keep sessions in-memory only.
**Decision**: P1-002 uses in-memory session store only. No YAML writes, no database, no file persistence. The API validates the contract and enforces the one-question-at-a-time rule, but all state lives in process memory.
**Consequences**: The API is testable and demonstrates the full intake workflow. Data is lost on process restart, which is acceptable for v0.1 local use. File persistence is deferred to a later slice (P1-003+). Prevents accidental active YAML mutation and premature persistence complexity.
**Alternatives**: Add YAML persistence in P1-002 (rejected — adds write-path complexity before API contract is validated; risk of accidental active YAML mutation). Add database persistence (rejected — premature, no multi-user need).

### Decision P1-003-01: Export path is service-only, not wired to API confirm endpoint

**Date**: 2026-05-19
**Status**: accepted
**Context**: P1-003 adds YAML export capability. The question was whether the confirm endpoint should automatically write YAML or whether export should be a separate, explicit operation.
**Decision**: Export is service-only. snapshot_export.py provides functions (snapshot_to_canonical_dict, snapshot_to_yaml, write_snapshot_yaml) but none are called by the confirm endpoint. write_snapshot_yaml requires an explicit target_path — no hardcoded alters/current/snapshot.yaml.
**Consequences**: Confirm remains in-memory and safe. Export is opt-in and explicit. The active snapshot.yaml is never mutated by the API. File writes only happen through deliberate function calls with explicit paths.
**Alternatives**: Auto-write on confirm (rejected — violates the "no automatic active YAML mutation" rule). Expose export as API endpoint (deferred to later slice — P1-003 is service/export contract only).

### Decision P2-001-01: Phase 2 starts with read-only loaders over the sealed Phase 1 active YAML chain

**Date**: 2026-05-19
**Status**: accepted
**Context**: Phase 2 begins with a read-only runtime foundation. Before adding any generation, runtime automation, or interactive systems, the system must be able to reliably read and validate its current governed artifacts.
**Decision**: Phase 2 starts with a read-only loader package that loads all 9 active YAML artifacts, validates them against the sealed baseline schema, and produces a summary — all without mutating any YAML file. The loader is testable from Python and returns ValidationResult (not exceptions) for semantic validation failures.
**Consequences**: The system gains a verified read-only interface to its governed artifacts. Future slices (P2-002+) can build CLI tools, validators, and read-only dashboards on top of this foundation. No generation, no mutation, no provider integration. The loader serves as a trust boundary between read-only and write operations.
**Alternatives**: Start with CLI tool (rejected — needs loader foundation first). Start with generation runtime (rejected — premature before read-only validation is stable). Start with database persistence (rejected — file-based governance is not yet validated for read access).

**Date**: 2026-05-19
**Status**: accepted
**Context**: P1-010 redesigns the Alter schema for active Phase 1 use. The Phase 0 template used nested structure (branch_ref as simple string, snapshot_ref as simple string). As backend services were implemented (P1-004 through P1-009), the nested structure proved awkward for API validation, database mapping, and cross-service references. The question was whether to keep the Phase 0 nested structure or flatten the schema.
**Decision**: Alter schema is flattened to active format. source_refs is a structured object containing branch_ref, snapshot_ref (and any future refs). quality_status is a top-level field tracking Alter quality state (e.g., "draft", "confirmed", "stale"). The Phase 0 _template.yaml remains inactive_template_only and is not modified. Active alters in Phase 1 use the flat schema exclusively.
**Consequences**: Flat schema is easier to validate, serialize, and reference across services. source_refs groups all references in one place, making dependency tracking explicit. quality_status enables lifecycle management without scanning nested fields. Phase 0 template remains as historical reference. Governance docs (QUALITY_GATES.md) updated to accept flat schema with source_refs/quality_status.
**Alternatives**: Keep nested Phase 0 structure (rejected — awkward for API validation and cross-service use). Separate source_refs into individual top-level fields (rejected — scatters references, harder to track). Remove quality_status (rejected — no lifecycle visibility without it).

### Decision P1-CLARIFY-01: P1-004 through P1-009 were controlled artifact writes, not backend runtime implementations

**Date**: 2026-05-19
**Status**: accepted
**Context**: P1-004 through P1-009 were originally described in governance docs as "Backend Service + API" implementations. Review revealed these were controlled YAML writes (file generation and schema validation), not running backend services with live API endpoints. The titles overstated the runtime capability.
**Decision**: P1-004 through P1-009 titles and descriptions are corrected to "Controlled YAML Write". They implemented file-based artifact generation and validation — not runtime backend services. The governance docs (PROJECT_BOARD, TASK_QUEUE, QUALITY_GATES) are updated to reflect the actual scope. This is a documentation accuracy fix, not a scope change.
**Consequences**: Governance docs now accurately describe what was implemented. Future readers will not mistake controlled YAML writes for live backend services. No code changes required — only documentation corrections.
**Alternatives**: Leave original "Backend Service + API" titles (rejected — creates false impression of runtime capability, undermines governance doc trustworthiness).

### Decision P3-001R2-01: Controlled mutation approval tokens are evidence signals, not shared secrets

**Date**: 2026-05-19
**Status**: accepted
**Context**: P3-001 introduced a fixed magic approval token (`p3-001-approved`) that was compared as a shared secret. This conflated approval evidence with authentication. The system needs to record that a human approved a mutation, not that a caller knows a secret.
**Decision**: Approval tokens are evidence signals. Any non-empty, non-whitespace token is accepted as approval evidence. The token is hashed (SHA-256) before storage. The raw token is never stored, logged, or exposed in API responses. Governance relies on explicit human confirmation plus audit trail, not on token matching.
**Consequences**: No hardcoded secret to leak. Audit trail records approval evidence (hash) without exposing the token. The system is simpler and more honest about what approval tokens represent.
**Alternatives**: Keep fixed magic token (rejected — conflates auth with governance, creates false sense of security). Require token to match a stored value (rejected — introduces secret management complexity inappropriate for a personal tool).

### Decision P3-001R3-01: Runtime audit logs committed only for approved real persist operations

**Date**: 2026-05-19
**Status**: accepted
**Context**: P3-001R2 introduced write_snapshot_with_audit which appends JSONL audit records. Earlier test runs accidentally wrote old-schema audit entries to docs/harness/phase3_write_audit.jsonl. These stale entries used the old schema (action/sha256_before/sha256_after) and targeted alters/current/snapshot.yaml, falsely implying approved production writes.
**Decision**: Runtime write audit logs are only committed when produced by an explicitly approved real persist operation. Test-generated or accidental audit logs must not be committed. The audit log file is not committed to the repository until a real human-approved persist occurs. Tests use monkeypatched paths to avoid writing to the committed audit log location.
**Consequences**: Audit evidence in the repository is trustworthy. Stale or test-generated logs cannot be mistaken for governance evidence. The audit log file remains gitignored or untracked until a real persist event occurs.
**Alternatives**: Commit all audit logs including test runs (rejected — pollutes governance evidence with non-approved entries). Delete audit log on every test run (rejected — test code should not modify production files).

### Decision P3-M2-01: Generation runtime starts as deterministic draft-only output

**Date**: 2026-05-19
**Status**: accepted
**Context**: P3-M2 introduces the first generation layer. The question was whether to start with provider-backed generation or deterministic template-based generation.
**Decision**: Generation runtime starts as deterministic, template-based, draft-only output. No LLM provider calls. All generated artifacts are drafts requiring human review. Drafts are never promoted to active state without passing through the controlled persist APIs from P3-M1. This proves generation boundaries before provider integration.
**Consequences**: Generation is predictable, testable, and auditable. Drafts are review inputs, not active state. Provider integration is deferred to a later phase with explicit approval.
**Alternatives**: Start with provider-backed generation (rejected — too many untested boundaries). Skip draft stage and generate directly to active (rejected — violates controlled mutation principles).

### Decision P3-M1R-01: Controlled write schemas must forbid extra fields

**Date**: 2026-05-19
**Status**: accepted
**Context**: P3-M1 review found that Branches and Alters schemas used plain `BaseModel` without `extra="forbid"`. This meant Pydantic silently ignored smuggled fields (calibration, archive, provider, dialogue, runtime, alter_generation) before service-level validation could check them. The service-level forbidden-field checks were therefore ineffective as a first defense.
**Decision**: All Branches and Alters request and nested schemas must use `model_config = ConfigDict(extra="forbid")`. This makes Pydantic reject any unrecognized fields at request validation time with a 422 error. Service-level validation remains as a second defense for already-parsed payloads.
**Consequences**: Smuggled forbidden fields are rejected at the API input layer. The defense is layered: schema-level (first) + service-level (second). The contract is explicit and testable.
**Alternatives**: Rely on service-level checks only (rejected — Pydantic swallows extra fields before service sees them). Add field allowlists manually (rejected — ConfigDict(extra="forbid") is idiomatic and comprehensive).

### Decision P3-M2R-01: Generation draft runtime must integrate with real active YAML loader shape

**Date**: 2026-05-19
**Status**: accepted
**Context**: P3-M2 review found that generation draft service used dict-style `.get("snapshot")` but the real `load_active_yaml_chain()` returns an `ActiveYamlChain` dataclass with `.snapshot`, `.branches`, etc. attributes. Additionally, real snapshot YAML is wrapped: `{"snapshot": {"intake_status": {...}}}`, so `snapshot["intake_status"]` fails on the real shape. API tests only monkeypatched a simplified dict fixture, masking both issues.
**Decision**: Add `normalize_active_chain()` to handle both `ActiveYamlChain` dataclass and dict shapes. Add `extract_snapshot_body()` to handle wrapped/unwrapped snapshot YAML. Add `extract_branch_list()` to extract branches from real YAML structure. API now returns HTTP 500 for loader failure and HTTP 400 for validation failure. Service type hints accept `ActiveYamlChain | dict | None`. Tests include real loader smoke test that works without monkeypatching `load_active_yaml_chain`.
**Consequences**: Generation draft runtime works with both test fixtures and real production loader. Validation catches wrapped snapshot shape. Error responses are structured by failure type.
**Alternatives**: Require all callers to pass pre-normalized dict (rejected — forces callers to know internal shape). Only support dict shape (rejected — real loader returns dataclass, runtime would break).

### Decision P3-M3-01: Promotion package is not active state

**Date**: 2026-05-19
**Status**: accepted
**Context**: Draft review can prepare payloads for controlled persist APIs, but the question was whether the promotion package itself constitutes active state or requires separate controlled persist.
**Decision**: Promotion package is a review artifact, not active state. Draft review can prepare branches and alters payloads, but cannot itself mutate active YAML. Actual active YAML mutation must still happen through previously approved controlled persist APIs (/branches/persist, /alters/persist/{alter_id}, /alters/persist-batch). This preserves separation between generation/review and active-state mutation.
**Consequences**: Three-step pipeline: generate draft → review and prepare promotion → controlled persist. No single step can both prepare and write active state.
**Alternatives**: Allow promotion package to directly write active YAML (rejected — violates controlled mutation principles). Skip promotion package and review directly writes (rejected — no separation between review and mutation).

### Decision P3-M4-01: Promotion orchestration plan is not promotion execution

**Date**: 2026-05-19
**Status**: accepted
**Context**: P3-M4 introduces an orchestration planning layer. The question was whether this layer should execute promotion or only plan it.
**Decision**: Promotion orchestration plan is not promotion execution. The system can plan active promotion steps, evidence requirements, and rollback requirements without mutating active state. This preserves the separation between review, planning, and execution. All steps have execution_allowed_in_p3_m4=false. Human final approval is required before any future execution.
**Consequences**: Four-step pipeline: generate draft → review and prepare promotion → plan orchestration → controlled persist. Each step is separate and requires different authorization. Planning is auditable without risk.
**Alternatives**: Allow orchestration plan to execute directly (rejected — violates controlled mutation principles). Skip planning and execute directly from promotion package (rejected — no separation between review and execution planning).

### Decision P3-M5-01: Execution gate is not live execution

**Date**: 2026-05-19
**Status**: accepted
**Context**: P3-M5 introduces an execution gate layer. The question was whether this layer should perform live promotion or only validate readiness.
**Decision**: Execution gate is not live execution. The system can validate whether a promotion orchestration plan is eligible for future active execution — checking prerequisites, running dry-run compatibility checks, generating execution packets — without mutating active state. execution_allowed_now=false, live_execution_allowed_in_p3_m5=false, requires_p3_m6_live_execution=true. P3-M6 is required for actual live execution.
**Consequences**: Five-step pipeline: generate draft → review and prepare promotion → plan orchestration → execution gate → controlled persist. Each step is separate and requires different authorization. The gate provides auditable evidence of readiness without risk.
**Alternatives**: Allow execution gate to perform live promotion (rejected — violates controlled mutation principles). Skip gate and execute directly from orchestration plan (rejected — no validation of readiness before execution).

### Decision P3-M6-01: Live execution defaults to dry_run and requires explicit safe configuration

**Date**: 2026-05-19
**Status**: accepted
**Context**: P3-M6 introduces the first layer that CAN call controlled persist services (write_branches_with_audit, write_alter_batch_with_audit). The question was how to prevent accidental live execution while still enabling the full pipeline.
**Decision**: Live execution defaults to dry_run mode. The API endpoint rejects live mode when LIVE_EXECUTION_ENABLED=false (HTTP 403). Live execution requires explicit path_overrides dict (branches_target_path, alters_dir, backup_dir, audit_log_path) — without them, the endpoint returns a rejected report. Token hash must match execution_packet.final_approval_token_hash when require_matching_gate_token=true (default). All persist calls go through controlled persist service functions — no direct file writes.
**Consequences**: The five-step pipeline is complete: generate draft → review and prepare promotion → plan orchestration → execution gate → controlled live execution → controlled persist APIs. Each step is separate and requires different authorization. Accidental live execution is prevented by multiple layers: mode default, server flag, path_overrides requirement, and token hash matching.
**Alternatives**: Default to live mode (rejected — too risky for accidental execution). Skip path_overrides requirement (rejected — allows writing to hardcoded paths, defeats testability). Disable token hash matching by default (rejected — weakens gate integrity).

### Decision P3-M6R-01: Payload models use extra="allow" to preserve full active YAML data

**Date**: 2026-05-19
**Status**: superseded by P3-M6R2-01
**Context**: P3-M7 live execution failed because AlterPayload(extra="forbid") and BranchDiscoveryPayload/Status(extra="forbid") stripped extra fields during re-persist, causing semantic diffs in active YAML files.
**Decision**: Change AlterPayload, BranchDiscoveryPayload, and BranchDiscoveryStatus from extra="forbid" to extra="allow". API request models (AlterPersistRequest, AlterBatchPersistRequest, BranchesPersistRequest) retain extra="forbid" to reject smuggled fields at the API boundary. Payload models accept extra fields to preserve full alter/branch data during controlled re-persist.
**Consequences**: Active YAML data is fully preserved during live execution. API boundary still rejects unknown fields. Test data for payload models must include all required fields.

### Decision P3-M6R2-01: Raw dict re-persist preserves extras without weakening API schemas

**Date**: 2026-05-19
**Status**: accepted
**Context**: P3-M6R changed AlterPayload/BranchDiscoveryPayload/BranchDiscoveryStatus from extra="forbid" to extra="allow", which weakened the API smuggling boundary from P3-M1R. GPT BLOCKED the commit because extra="allow" on nested payload models allows smuggled fields to pass through the API boundary.
**Decision**: Revert all payload models to extra="forbid". Use raw dict functions (write_alter_raw_batch_with_audit, write_branches_raw_with_audit) for the re-persist path in execute_promotion_live(). These functions validate required fields via dict checks, then write the raw dict directly to YAML via yaml.safe_dump(), preserving all extra fields without going through Pydantic model serialization (which strips extras via model_dump()). API boundary models remain extra="forbid".
**Consequences**: API smuggling boundary preserved (all models extra="forbid"). Active YAML extras preserved during live execution (raw dict round-trip). Governance validation still enforced on raw dicts (required fields, forbidden fields). No Pydantic model needed for re-persist path.

### Decision P3-M7-01: First live promotion run must be semantic no-op

**Date**: 2026-05-19
**Status**: accepted
**Context**: Before using the live executor for new semantic content, the system must prove that controlled live mutation, backup, audit, validation, and rollback evidence work on existing active state.
**Decision**: P3-M7 uses semantic no-op live promotion — the promotion package is built from the current active YAML without introducing new branch meaning. Active YAML may only change due to canonical controlled-persist formatting. Semantic YAML equivalence must be proven before and after.
**Consequences**: Full controlled mutation chain validated end-to-end: active YAML → no-op promotion package → orchestration plan → execution gate → live execution runtime → controlled persist services → active YAML validation → evidence report.

### Decision P3-M8-01: Phase 3 closeout is read-only and evidence-based

**Date**: 2026-05-19
**Status**: accepted
**Context**: After the first controlled live no-op run (P3-M7) and schema boundary repair (P3-M6R2), the Phase 3 mutation implementation chain is complete. The project must seal the mutation baseline by verifying evidence and boundaries, not by adding more mutation capability.
**Decision**: P3-M8 implements a read-only closeout gate that runs 9 verification checks (active YAML chain, evidence files, P3-M7 evidence, smuggling boundary, raw dict path, live execution safety, runtime artifacts, audit logs, governance status). The closeout gate does not write active YAML, does not call live execution, does not call controlled persist services. It produces a closeout report and evidence artifact as the Phase 3 sealed baseline candidate. Final sealing requires human/GPT review.
**Consequences**: Phase 3 is sealed with read-only evidence. P4-000 (Phase 4 scope) is blocked until human/GPT review confirms the closeout. No further mutations possible without explicit Phase 4 authorization.

### Decision P3-M8R2-01: Closeout evidence must distinguish tracked raw audit logs from ignored local runtime files

**Date**: 2026-05-19
**Status**: accepted
**Context**: The original closeout check `check_no_raw_audit_logs_committed` used filesystem presence in docs/harness to decide FAIL. This was too coarse — local untracked/ignored runtime audit files (e.g. phase3_write_audit.jsonl) should not block Phase 3 sealing.
**Decision**: Use `git ls-files` from repo_root to check whether audit jsonl files are tracked by git. FAIL only when raw audit jsonl files are tracked. WARN when audit jsonl files exist locally but are untracked/ignored. PASS when none exist. Same git-aware logic applied to `check_no_runtime_artifacts_committed`.
**Consequences**: Closeout evidence is truthful about what is actually committed vs what is just a local runtime artifact. PASS_WITH_NOTES is a valid sealed state when only ignored runtime drafts exist.

### Decision P4-000-01: Phase 4 begins with Dialogue + Calibration Loop, not broad productization

**Date**: 2026-05-19
**Status**: accepted
**Context**: Phase 3 proved controlled mutation runtime works end-to-end. Phase 4 must decide what comes next — broad product UI, database, provider integration, or user-facing calibration workflow.
**Decision**: Phase 4 focuses on Dialogue + Calibration Loop + Minimal User Workflow. This means P4-M1 (Alter Dialogue Runtime), P4-M2 (Reality Score Form/API), P4-M3 (Drift Calculation), P4-M4 (Calibration History Query), P4-M5 (Rubric Delta Suggestion), P4-M6 (Archive Mechanism), P4-M7 (Checkpoint Regeneration Plan). Minimal frontend limited to dialogue, reality score form, calibration history. Broad product UI, branch map, database, and provider integration are excluded.
**Consequences**: Phase 4 validates the user-facing calibration loop before broader expansion. Scope is intentionally narrow to prevent premature productization.

### Decision P4-000-02: Real branch/alter semantic replacement remains blocked until explicitly approved

**Date**: 2026-05-19
**Status**: accepted
**Context**: P3-M7 proved semantic no-op live mutation works. True semantic promotion (new branch/alter meaning entering active state) has different safety requirements.
**Decision**: Direct replacement of active branch/alter semantics remains blocked until a later explicitly approved slice. No LLM output may jump directly to confirmed state. First allowed semantic writes are limited to reality_score records, calibration_history records, rubric_delta_suggestion records, archive/checkpoint metadata, and explicitly saved dialogue session logs.
**Consequences**: Semantic promotion gets its own review and safety gate. This prevents accidental semantic drift through automated paths.

### Decision P4-M1-01: Alter Dialogue Runtime is read-only and provider-free in first slice

**Date**: 2026-05-19
**Status**: accepted
**Context**: Phase 4 begins with dialogue capability. The first question was whether to build full provider-backed dialogue immediately or establish safe context packaging first.
**Decision**: P4-M1 implements read-only dialogue context and prompt packet building only. No LLM provider is called. No assistant replies are generated. No dialogue logs are persisted. provider_ready is always false. The runtime validates active alter contracts, builds dialogue context with scope boundaries, and returns prompt packets for downstream use.
**Consequences**: Phase 4 establishes safe dialogue context packaging before provider-backed replies or saved dialogue logs. This prevents premature provider integration and ensures alter persona consistency is validated before any LLM interaction.

### Decision P4-CAL-LOOP-MVP-01: Calibration loop records user submissions and keeps drift evidential

**Date**: 2026-05-20
**Status**: accepted
**Context**: P4-CAL-LOOP-MVP combines dialogue contract hardening with P4-M2/M3/M4. The blocker was summary-only dialogue injection, and the calibration loop needed a backend contract without broad productization or automatic mutation.
**Decision**: Prompt packets must include the complete loaded alter YAML. Reality scores are explicit user-submitted records written only under `alters/calibration/scores/score_*.yaml`. Drift calculation requires supplied expected and actual scores and returns response-only evidence. Calibration history is read-only and may derive drift in memory. No endpoint writes `alters/current/**` or `alters/calibration/rubric.yaml`, and no provider, frontend, database, archive, promotion, or regeneration path is added.
**Consequences**: P4 has a usable backend calibration loop while preserving Phase 3 mutation boundaries. Drift can inform review but cannot trigger automatic regeneration or rubric evolution.

### Decision P4-M5-01: Rubric delta is suggestion-only and cannot modify rubric.yaml

**Date**: 2026-05-20
**Status**: accepted
**Context**: P4-M5 needs to identify repeated expected-vs-actual mismatch patterns without destabilizing the calibration rubric.
**Decision**: Rubric delta output is a `pending_review` suggestion only. It may be saved under `alters/calibration/rubric_delta_suggestions/`, but `rubric_write_allowed` is always false and `alters/calibration/rubric.yaml` is never modified.
**Consequences**: Drift can inform future human review while preserving rubric stability.

### Decision P4-M6-01: Archive creation is explicit-only and copies state without modifying source

**Date**: 2026-05-20
**Status**: accepted
**Context**: Future major writes require a rollback evidence package, but archive creation must not be silent or alter current state.
**Decision**: Archive planning is read-only. Archive creation occurs only through an explicit request and copies approved source files into `alters/archive/checkpoints/archive_*` with sha256 manifest entries. Source files are unchanged.
**Consequences**: Archive packages support future rollback review without becoming hidden mutation or rollback execution.

### Decision P4-M7-01: Checkpoint regeneration is plan-only; no active regeneration

**Date**: 2026-05-20
**Status**: accepted
**Context**: High drift should trigger structured review, not automatic branch/alter replacement.
**Decision**: Checkpoint regeneration produces a `pending_review` plan with execution disallowed on every step. `regeneration_allowed_now` and `active_write_allowed` are always false. No provider, generation, or active YAML write is called.
**Consequences**: High drift creates a governance artifact for review while semantic promotion remains blocked until a later approved slice.

### Decision P4-CLOSEOUT-01: Phase 4 closeout seals backend calibration loop, not full productization

**Date**: 2026-05-20
**Status**: accepted
**Context**: P4-FINAL completes the remaining planned backend calibration scope, but does not authorize P5 work.
**Decision**: Phase 4 closeout verifies P4-M1R through P4-M7, no provider/frontend/database work, no active YAML/rubric diff, and no committed raw runtime records. It establishes a sealed backend calibration loop candidate only.
**Consequences**: P5-000 remains blocked pending GPT/human review and a separate boundary plan.

### Decision P5-000-01: P5 is local MVP productization, not hosted SaaS

**Date**: 2026-05-20
**Status**: accepted
**Context**: P5 scope must be bounded to avoid scope creep into cloud deployment, multi-user auth, or production infrastructure.
**Decision**: P5 is defined as Local Product MVP — single-user, local-only, file-based storage. No cloud deployment, no production auth, no billing, no mobile app.
**Consequences**: P5 delivers a usable local loop without production complexity. P6 will address production concerns when ready.

### Decision P5-M2-01: Provider access must go through provider gateway only

**Date**: 2026-05-20
**Status**: accepted
**Context**: Prevents scattered provider SDK imports and inconsistent error handling across feature modules.
**Decision**: All provider calls go through a single provider_gateway service. No feature module directly imports provider SDKs. Default mode is mock.
**Consequences**: Centralized provider control, easier testing, no SDK dependency leakage.

### Decision P5-M3-01: Provider dialogue output does not persist or mutate by default

**Date**: 2026-05-20
**Status**: accepted
**Context**: Provider replies are simulated and should not be treated as facts or automatically persisted.
**Decision**: save_session defaults to false. Provider output never writes active YAML. Saved sessions go to alters/product/sessions/ (ignored by default).
**Consequences**: User must explicitly opt-in to session persistence. Provider output is clearly separated from active state.

### Decision P5-M4-01: Frontend may call only safe product APIs

**Date**: 2026-05-20
**Status**: accepted
**Context**: Frontend must not have access to dangerous endpoints that could mutate active state.
**Decision**: Frontend calls only safe product APIs (/product/*, /provider-dialogue/*, /calibration-loop/*, /rubric-delta/*, /checkpoint-regeneration/*). No calls to promotion-live-execution, controlled persist, or archive create.
**Consequences**: Frontend is safe by construction. Dangerous operations remain API-only with explicit confirmation.

### Decision P5-M5-01: YAML remains default storage; database migration deferred

**Date**: 2026-05-20
**Status**: accepted
**Context**: Database migration would add significant complexity and is not needed for local MVP.
**Decision**: YAML remains the default storage backend. Storage boundary module describes path classifications. SQLite/PostgreSQL deferred to a future phase.
**Consequences**: Simpler implementation, no database dependency. Migration path documented for future phase.

### Decision P5-M7-01: P5 closeout verifies productization boundaries, not production readiness

**Date**: 2026-05-20
**Status**: accepted
**Context**: P5 is a local MVP, not a production product. Closeout should verify boundaries, not production readiness.
**Decision**: Phase 5 closeout checks: provider gateway default safe, no secrets committed, no active YAML diff, no rubric diff, frontend safety, storage boundary, provider dialogue defaults, P5 docs complete, no raw runtime artifacts.
**Consequences**: Clear distinction between local MVP verification and production readiness assessment.

### Decision P6-000-01: Personal long-term use over public productization

**Date**: 2026-05-20
**Status**: accepted
**Context**: After P5 local MVP completion, the question is what P6 should address — public productization or personal long-term use hardening.
**Decision**: P6 is defined as personal long-term use hardening, not public productization. The system has not been validated by real usage. P6 focuses on Charlie's actual usage patterns, not market features.
**Consequences**: P6 scope is constrained to personal use validation. Public productization is deferred until after P6 behavior validation passes.

### Decision P6-000-02: Behavior change as success standard

**Date**: 2026-05-20
**Status**: accepted
**Context**: P6 needs a success criterion. Code completion alone would be productivity theatre.
**Decision**: P6 success is measured by behavior change, not feature completion. Criteria: action_alignment_score_improves, repeated_negative_patterns_reduce, primary_correction_completion_rate_improves.
**Consequences**: P6 requires a 4-week real-use validation window. P6_CODE_COMPLETE is not sufficient for sealing.

### Decision P6-000-03: Obsidian raw note as primary evidence

**Date**: 2026-05-20
**Status**: accepted
**Context**: Weekly review needs an evidence source. System-generated summaries risk inventing facts.
**Decision**: Obsidian raw weekly note is the primary evidence source. System extracts structure from raw notes but cannot invent weekly facts. Dual-layer truth: raw note wins in conflicts.
**Consequences**: System cannot fabricate facts. Raw note + edit diff wins over derived calibration record. Human edits require correction_note.

### Decision P6-000-04: Action alignment as primary metric

**Date**: 2026-05-20
**Status**: accepted
**Context**: P6 needs a primary metric to measure weekly progress.
**Decision**: `action_alignment` is the primary metric — whether actions match the user's endorsed direction. Three-dimensional scoring: direction_alignment, execution_consistency, avoidance_level.
**Consequences**: All scoring and review centers on alignment between stated direction and actual action. Each session requires one_action_evidence, one_avoidance_or_friction_evidence, and one_next_correction.

### Decision P6-000-05: Dual-layer output

**Date**: 2026-05-20
**Status**: accepted
**Context**: Weekly review output needs to serve both human understanding and system tracking.
**Decision**: P6 produces two-layer output: human-readable review_note and machine-readable calibration_record. Both are required per session.
**Consequences**: Neither layer is optional. review_note serves narrative review; calibration_record serves pattern tracking.

### Decision P6-000-06: 4-week validation window

**Date**: 2026-05-20
**Status**: accepted
**Context**: P6 needs a minimum validation period before sealing.
**Decision**: P6 requires 4 weeks of real use before sealing. Required: 4 weekly reviews, at least 4 calibration records, at least 1 monthly pattern review, measurable change in action alignment / negative patterns / primary correction completion.
**Consequences**: P6 cannot be sealed after code completion alone. One week is noise; four weeks shows patterns.

### Decision P6-000-07: Provider default disabled/mock

**Date**: 2026-05-20
**Status**: accepted
**Context**: P6 weekly review could use a real LLM provider, but this introduces dependency and truth-confusion risks.
**Decision**: Provider remains disabled or mock by default. Real provider requires explicit user configuration. No API key committed. No default real provider calls. Weekly review must run with mock. Real provider output cannot auto-write active YAML or auto-generate reality score.
**Consequences**: P6 is self-contained. Provider output is never mistaken for system truth.

### Decision P6-000-08: No-improvement requires usage integrity audit first

**Date**: 2026-05-20
**Status**: accepted
**Context**: If no behavior improvement after 4 weeks, the system could be wrong or the usage could be dishonest.
**Decision**: If no improvement after 4 weeks, first audit usage integrity: weekly notes completed honestly, calibration records created, primary corrections set, failure reviews honest, self_deception_risk not softened, sessions not skipped too often. If usage invalid, fix usage behavior. If usage valid but no improvement, decide redesign or stop expansion.
**Consequences**: Prevents adding features to solve a usage honesty problem. Forces honest assessment before redesign.

### Decision P6-CODE-01: Code completion is not behavior validation

**Date**: 2026-05-20
**Status**: accepted
**Context**: P6-M1 through P6-M11 runtime code can be implemented before Charlie has accumulated four weeks of real-use data.
**Decision**: P6 runtime code may reach code_complete_pending_review while P6_BEHAVIOR_VALIDATED remains unavailable. The behavior validation gate returns insufficient data until the required real-use evidence exists, and the P6 closeout gate remains blocked unless the latest behavior validation outcome is P6_BEHAVIOR_VALIDATED.
**Consequences**: The backend can be exercised immediately, but P6 cannot be sealed by implementation work alone. This preserves the P6 success standard: behavior change after four weeks, not feature completion.
**Alternatives**: Mark P6 complete after runtime implementation (rejected because it violates P6-000-06 and R-099).

### Decision P6-CODE-R1-01: Behavior validation must verify persisted evidence

**Date**: 2026-05-20
**Status**: accepted
**Context**: Review found that behavior validation could be faked by sending arbitrary weekly/calibration/pattern IDs plus true booleans.
**Decision**: Behavior validation must load and verify persisted P6 runtime evidence before returning P6_BEHAVIOR_VALIDATED. It rejects unknown IDs, requires at least 4 weekly review records, at least 4 calibration records linked to those weekly reviews, at least 1 real 4-week pattern review, and a 4-week evidence window. Phase6 closeout re-verifies persisted validation evidence instead of trusting the outcome field alone.
**Consequences**: Fake or manually written validation records cannot seal P6. Real behavior validation remains possible once four weeks of persisted evidence exists.
**Alternatives**: Trust request-supplied IDs and booleans (rejected because it violates the P6 behavior validation standard).

### Decision P6-ENDGAME-01: Endgame orchestration is allowed but cannot seal P6

**Date**: 2026-05-20
**Status**: accepted
**Context**: P6 runtime code is complete and merged, but P6 still needs real 4-week evidence before behavior validation and closeout. Without an endgame runbook, each week would require a new implementation slice and operators could confuse automation progress with validation progress.
**Decision**: P6 endgame can be orchestrated end-to-end with runbooks, templates, helper scripts, and governance tracking. The final seal still requires real persisted evidence for 4 weekly reviews, 4 calibration records, at least 1 pattern review, a real 4-week window, `P6_BEHAVIOR_VALIDATED`, and phase6 closeout `PASS`.
**Consequences**: Operators can run the same process each week without new implementation scope, while P6 remains blocked until real evidence exists. Helper scripts may create runtime records only from Charlie-provided real weekly notes, and raw records remain gitignored unless explicitly sanitized as evidence.
**Alternatives**: Require a new implementation slice each week (rejected because it adds coordination overhead without changing runtime behavior). Allow automation to seal P6 after setup (rejected because it violates the 4-week real-use validation standard).

### Decision P7-000-01: P7 is local app distribution, not cloud productization

**Date**: 2026-05-20
**Status**: accepted
**Context**: P6 real use should not require coding tools, but distribution work could drift into SaaS, cloud deployment, multi-user auth, or public productization.
**Decision**: P7 is defined as local app distribution for Linux/Ubuntu/Debian-style systems. It targets an installable local application with backend, frontend, provider configuration, runtime data directory, desktop launcher, and `.deb` packaging. It excludes cloud, SaaS, multi-user accounts, production auth, mobile apps, Windows/macOS packaging, and P8 work.
**Consequences**: P7 can make the system easier to use locally without expanding the product boundary beyond a single-user local application.

### Decision P7-000-02: Packaged mode must use user data dirs, not repo runtime dirs

**Date**: 2026-05-20
**Status**: accepted
**Context**: Repo-based P6 runtime paths are acceptable for development, but an installed app cannot depend on a writable repository checkout.
**Decision**: Packaged mode writes runtime data under `~/.local/share/alters-lab`, config under `~/.config/alters-lab`, and logs under `~/.local/state/alters-lab/logs`. Application code installs under `/opt/alters-lab`. Dev mode may remain repo-compatible, but active YAML and rubric protections apply in both modes.
**Consequences**: P7-M1 must introduce a runtime config/path resolver and update production writes before packaging work proceeds.

### Decision P7-000-03: P7 enables P6 validation but does not replace it

**Date**: 2026-05-20
**Status**: accepted
**Context**: P7 exists because real P6 use should be possible outside coding tools, but P6 validation requires real weekly evidence over time.
**Decision**: P7 may enable P6 real-use validation by making the app installable and launchable. P7 does not mark P6 behavior validated, does not seal P6, and must not fabricate weekly review, calibration, pattern review, or behavior validation records.
**Consequences**: P6 remains CODE_COMPLETE / NOT_VALIDATED / NOT_SEALED until verified real-use evidence satisfies the P6 gate.

### Decision P7-000-04: Provider is explicit and secret-redacted

**Date**: 2026-05-20
**Status**: accepted
**Context**: Local app distribution requires provider configuration, but secrets and provider output can compromise safety if exposed or treated as truth.
**Decision**: Provider defaults to disabled/mock. Real provider mode must be explicit. API keys are stored only in local secret storage, never committed, never returned by API responses, and never logged. Provider output is not persistent by default, never writes active YAML, and never auto-generates reality scores.
**Consequences**: P7-M4 must include redacted provider status and a local secret storage strategy before real provider use is considered usable.

### Decision P7-000-05: Debian package preserves user data on upgrade/uninstall

**Date**: 2026-05-20
**Status**: accepted
**Context**: Package lifecycle scripts can accidentally overwrite or delete the user data needed for P6 real-use validation.
**Decision**: The `.deb` package installs app code and launch integration only. User config, secrets, data, and logs stay under the user's home directory and are preserved on upgrade and uninstall unless a future explicit purge path is separately approved.
**Consequences**: P7-M5 through P7-M7 must treat user data preservation as a release-blocking packaging requirement.

### Decision P7-M1-01: Runtime layout resolver separates dev repo paths from packaged user data paths

**Date**: 2026-05-21
**Status**: accepted
**Context**: P6 runtime helpers were repo-rooted, which is suitable for development but unsuitable for an installed local app. P7 packaging needs a single path resolver before local server, launcher, and `.deb` work proceed.
**Decision**: P7-M1 introduces a runtime layout resolver with `dev` and `packaged` modes. Dev mode remains repo-compatible and preserves explicit `repo_root`/`tmp_path` behavior. Packaged mode resolves config to `~/.config/alters-lab/config.yaml`, runtime data to `~/.local/share/alters-lab/product`, logs to `~/.local/state/alters-lab/logs`, and secrets fallback to `~/.config/alters-lab/secrets.yaml`. Runtime safety flags for active YAML, rubric, and provider output remain false.
**Consequences**: P6/P7 runtime helpers can be exercised in packaged mode without requiring writable repo paths, while existing dev tests and helper tools keep working. P7-M2 can now focus on serving built frontend assets from FastAPI.

### Decision P7-M2-01: FastAPI is the unified local server for API and built frontend in packaged mode

**Date**: 2026-05-21
**Status**: accepted
**Context**: Packaged local app use should not require a separate Vite dev server. The backend already owns the local API and runtime layout; P7 needs one process that can serve API routes and built frontend assets.
**Decision**: FastAPI serves existing API routes plus built React frontend assets. API routers are registered before frontend fallback. Dev mode resolves frontend dist to `apps/web/dist`; packaged mode resolves it from app root, such as `/opt/alters-lab/web/dist`. Missing frontend dist is non-fatal and reports `frontend_available=false`.
**Consequences**: P7-M3 can implement a CLI launcher around one local server process instead of coordinating separate backend and Vite servers.

### Decision P7-M3-01: Local app launcher controls start/stop/status/open/doctor without coding tools

**Date**: 2026-05-21
**Status**: accepted
**Context**: P7 requires real local use without Codex, Claude Code, curl, pytest, or manual uvicorn commands. P7-M2 established one server process for API and frontend.
**Decision**: P7-M3 adds a local launcher CLI with `start`, `stop`, `status`, `open`, and `doctor`. The launcher defaults to `127.0.0.1:18790`, runs `python -m uvicorn alters_lab.main:app`, writes PID/log files under runtime state/log dirs, supports json/dry-run modes, and keeps P6 validation/seal flags false.
**Consequences**: P7-M4 can assume a local app can be started and inspected through launcher commands before adding provider configuration UI/API.

### Decision P7-M4-01: Provider configuration is local, explicit, redacted, and non-mutating

**Date**: 2026-05-21
**Status**: accepted
**Context**: P7 local app use needs provider configuration without turning provider output into system truth or leaking user secrets.
**Decision**: P7-M4 stores non-secret provider settings in local config and API keys only in optional keyring storage or a chmod `0600` fallback secrets file. Real `openai-compatible-http` mode requires explicit user configuration. API responses and frontend status are redacted. Provider configuration tests are dry-run/no-network by default. Provider output cannot persist by default, write active YAML, or generate reality scores.
**Consequences**: The local app can expose provider settings safely while preserving P6 behavior validation boundaries. P7-M5 may package the app without embedding or owning user secrets.

### Decision P7-M5-01: Debian package installs app code and CLI only; user data remains user-owned

**Date**: 2026-05-21
**Status**: accepted
**Context**: P7 needs an installable Debian package, but package lifecycle mistakes could overwrite P6 real-use evidence, provider secrets, config, or logs.
**Decision**: The Debian package build stages application code under `/opt/alters-lab`, frontend assets under `/opt/alters-lab/web/dist`, a package-local Python venv under `/opt/alters-lab/.venv`, and a CLI launcher under `/usr/bin/alters-lab`. User config, secrets, data, logs, raw P6 runtime records, node_modules, and `.env` files are excluded. Maintainer scripts do not create root-owned user config, start services, write secrets, or delete user home data.
**Consequences**: P7-M6 can add desktop integration on top of a package-owned launcher while P7-M7 still owns deeper upgrade/uninstall safety and backup/export behavior.

### Decision P7-M6-01: Desktop integration launches existing local CLI and does not own runtime state

**Date**: 2026-05-21
**Status**: accepted
**Context**: P7 local app use should work from the desktop app menu, but desktop integration must not introduce a second launcher path or hidden runtime behavior.
**Decision**: The desktop entry is package-owned, installed to `/usr/share/applications/alters-lab.desktop`, and launches `alters-lab open`. The icon is a project-owned SVG staged under the hicolor scalable app icon path. The desktop file contains no repo checkout paths, user-home paths, shell expansion, or secrets.
**Consequences**: Desktop launch reuses the existing CLI and runtime layout. P7-M7 can focus on upgrade/remove and user data preservation rather than another launch mechanism.

### Decision P7-M7-01: Upgrade/uninstall preserve user-owned state and backup excludes secrets by default

**Date**: 2026-05-21
**Status**: accepted
**Context**: Before release candidate testing, P7 must prove package lifecycle and backup behavior will not destroy or leak user-owned P6 evidence, config, logs, or secrets.
**Decision**: Package maintainer scripts preserve `~/.config/alters-lab`, `~/.local/share/alters-lab`, `~/.local/state/alters-lab`, and provider secrets on install, upgrade, remove, and purge. `alters-lab backup` backs up user data and config by default, excludes logs unless requested, and excludes secrets unless `--include-secrets --confirm-include-secrets include-secrets-in-backup` is supplied.
**Consequences**: P7-M8 can perform local app release candidate smoke testing with a backup/export path and explicit secret safety boundary.

### Decision P7-M8-01: Release-candidate smoke uses isolated package context and synthetic records only

**Date**: 2026-05-21
**Status**: accepted
**Context**: P7-M8 must prove the Debian package can run as a local app without mutating real user state or confusing smoke artifacts with P6 behavior validation.
**Decision**: The P7-M8 release-candidate smoke extracts the `.deb` with `dpkg-deb -x`, runs the packaged launcher/server in packaged mode with an isolated `HOME`, serves frontend assets from the package app root, and creates only synthetic weekly review/calibration records under the temporary user data directory. The smoke evidence records `p6_behavior_validated=false` and `p6_sealed=false`.
**Consequences**: P7-M8 can validate package integration and runtime path safety without requiring sudo, touching real user data, fabricating P6 evidence, or advancing P6 closeout.

### Decision P7-M9-01: Phase 7 closeout seals local app release candidate, not P6 behavior validation

**Date**: 2026-05-21
**Status**: accepted
**Context**: P7 closeout completes local Linux app distribution, but P6 behavior validation still depends on real weekly use over time.
**Decision**: P7-M9 seals Phase 7 as `LOCAL_APP_RELEASE_CANDIDATE`. This means local app distribution, Debian package build, CLI launcher, desktop integration, provider config safety, runtime layout, data safety, and package-context smoke are complete. It does not validate P6 behavior, does not seal P6, and does not authorize P8.
**Consequences**: The next recommended action is real P6 validation using the local app. P8 remains blocked until explicit human/GPT approval.

### Decision P7-R1-01: Weekly Review is the primary P6 frontend entry point

**Date**: 2026-05-21
**Status**: accepted
**Context**: P7 local app distribution was complete, but the frontend still looked like an engineering control panel. The backend weekly review flow existed but required scripts or direct API calls.
**Decision**: P7-R1 makes `Weekly Review` the primary P6 frontend entry point. The page walks the user through note ingest, extracted record review, weekly review start/complete, and action alignment scoring. `Reality Score` remains a manual/admin score submission page and explicitly points users to Weekly Review for real weekly review use.
**Consequences**: Real P6 weekly review evidence can now be created from the local app UI while preserving the boundary that P6 remains not behavior validated and not sealed.

### Decision P8-000-01: Real provider integration must be explicit, redacted, non-mutating, and audit-first

**Date**: 2026-05-27
**Status**: accepted
**Context**: P7 sealed the local app as a release candidate with mock-only provider support. Real provider integration requires careful safety boundaries to prevent secret leakage, accidental persistence, automatic scoring, and active YAML mutation.
**Decision**: P8 defines real provider integration as explicit opt-in, dry-run default, redacted status responses, no provider output persistence by default, no active YAML/rubric writes, user confirmation required for any persisted semantic output, audit metadata only (not raw secrets), and no background provider calls. P8 success is measured by safety and auditability, not merely by provider calls working.
**Consequences**: P8-M1 through P8-M7 implement provider capability within these boundaries. P6 behavior validation remains separate. P7 local app remains installable. Any future provider feature must pass through the safety boundary defined in `docs/harness/P8_PROVIDER_SAFETY_BOUNDARY.md`.

### Decision P8-M2-01: Real provider connectivity checks are explicit, redacted, non-generative by default, and separate from provider dialogue preview

**Date**: 2026-05-27
**Status**: accepted
**Context**: P8-M1 established the adapter contract with Literal-locked no-network safety fields. Real provider connectivity checking requires actual network calls but must be carefully gated to prevent accidental data leakage, prompt content exposure, or response persistence.
**Decision**: Create a separate connectivity-check module (schema/service/api) distinct from the adapter preview contract. The adapter preview remains no-network and Literal-locked. The connectivity check uses /models endpoint (preferred over /chat/completions), requires exact confirmation string for live checks, accepts an injectable http_client for testing, records only redacted metadata (no prompt content, no response body), and gates all network calls behind explicit user action. Status code mapping: 2xx=reachable+auth_ok, 401/403=reachable+auth_fail, timeout=unreachable.
**Consequences**: P8-M3 can build provider-backed dialogue on top of the connectivity foundation. The adapter preview contract remains untouched. Future connectivity improvements (e.g., model listing, latency benchmarks) can extend the connectivity module without affecting the adapter contract.

### Decision P8-M3-01: Provider-backed dialogue preview is preview-only, non-persistent, and user-triggered with exact confirmation

**Date**: 2026-05-27
**Status**: accepted
**Context**: P8-M2 established real provider connectivity checking. P8-M3 implements the first content-generating provider feature. Provider output must be unverified, non-persistent, and explicitly triggered to prevent accidental data mutation.
**Decision**: Create a dialogue preview module (schema/service/api) that uses /chat/completions endpoint with injectable http_client for testing. Output is preview-only (output_label="unverified_provider_preview"), never persisted (output_persisted=Literal[False], save_session=Literal[False], prompt_persisted=Literal[False], response_content_persisted=Literal[False]). Live generation requires live_generation=true and exact confirmation string "run-live-provider-dialogue-preview". Prompt capped at 8000 chars, system_prompt at 4000 chars, max_tokens 16-1200 (default 512), temperature 0.0-1.5 (default 0.7). persist_output and save_session blocked. No active YAML/rubric writes, no reality/action scores, P6 flags remain false.
**Consequences**: P8-M4 can build Weekly Review assistant on top of the dialogue preview foundation. The preview contract remains non-persistent. Future content-generating features must follow the same safety pattern: Literal-locked no-persist fields, injectable http_client, exact confirmation gating.

### Decision P8-M1-01: Provider adapter contract separates preview generation, network permission, persistence, and audit metadata

**Date**: 2026-05-27
**Status**: accepted
**Context**: P8-M1 needed a hardened adapter contract that separates concerns: which mode is active, whether network calls are permitted, whether output is persisted, and what audit metadata is recorded. The existing provider_config and provider_gateway modules manage configuration and actual calls, but neither provides a clean adapter-level contract with explicit safety guarantees.
**Decision**: Create a separate provider adapter module (schema/service/api) that sits above provider_config and below provider_gateway. The adapter contract handles: mode dispatch (disabled/mock/openai-compatible-http), request validation (live_check and persist_output blocked in P8-M1), deterministic mock preview, dry-run openai preview without network, audit event generation (metadata only, no raw prompt/response/secrets), and safety flag enforcement. All responses include explicit flags: network_call_made, output_persisted, active_yaml_modified, rubric_modified, reality_score_created, action_alignment_created, p6_behavior_validated, p6_sealed.
**Consequences**: P8-M2 can extend the adapter to enable live_check and real connectivity. P8-M3 can build provider-backed dialogue on top of the adapter contract. Safety guarantees are enforceable by tests rather than convention.

### Decision P8-M4-01: Weekly Review Assistant can suggest text, but user remains the only actor allowed to submit review content or scores

**Date**: 2026-05-27
**Status**: accepted
**Context**: P8-M4 adds optional provider assistance inside the Weekly Review flow. The provider should help draft suggestions but must never auto-submit, auto-score, or persist output. The user must manually edit/confirm anything that becomes part of the weekly review record.
**Decision**: Weekly review assistant reuses provider_dialogue_preview for actual provider calls (no separate unsafe path). Advisory-only suggestions with suggestion_persisted=Literal[False], weekly_review_completed=Literal[False], action_alignment_created=Literal[False]. Frontend provides copy-only buttons that fill local form fields but never auto-submit. live_generation requires exact confirmation="run-live-weekly-review-assistant".
**Consequences**: Provider suggestion is unverified and advisory. User retains full control over review submission. No new provider code paths needed — reuses existing dialogue preview safety gates.

### Decision P8-M5-01: P8 product validation uses package-context isolated HOME smoke by default; live provider checks remain optional and explicitly gated

**Date**: 2026-05-27
**Status**: accepted
**Context**: P8-M5 needs to validate the full local app product path after P8 provider features. Real provider calls should not run by default in smoke tests. Package-context validation must use isolated HOME to avoid mutating host state.
**Decision**: P8 E2E smoke script uses dpkg-deb -x into isolated temp install root with isolated HOME. All provider paths tested in mock/dry-run mode. Live provider support exists as optional flags (--allow-live-provider, --live-provider-confirmation) but is never invoked by default. Evidence is redacted (temp paths, no secrets, no raw provider output).
**Consequences**: Smoke evidence proves product paths work without risking real provider calls or host state mutation. Live provider smoke can be explicitly invoked by human when needed.

### Decision P9-000-01: P9 is release hygiene, not feature work

**Date**: 2026-05-27
**Status**: accepted
**Context**: P8 sealed the local app as REAL_PROVIDER_READY_LOCAL_APP. The app has backend, frontend, provider integration, Debian packaging, and CLI launcher. Before any real release or further feature work, the app needs install/uninstall docs, onboarding guides, troubleshooting docs, and a release checklist.
**Decision**: P9 is defined as release hygiene and install readiness. It adds documentation, verification, and onboarding — not new features. P9 excludes SaaS/cloud deployment, multi-user support, mobile app, Windows/macOS packaging, automatic P6 validation, provider output persistence, and active YAML/rubric mutation.
**Consequences**: P9 turns the sealed local app into a usable personal release without expanding the product boundary. P9-M1 (install docs) requires explicit approval before implementation begins.

### Decision P10-000-01: P10 is operational cutover, not feature expansion

**Date**: 2026-05-27
**Status**: accepted
**Context**: P9 sealed. P6 validation requires real usage data. Need to define what happens between "product ready" and "validation starts."
**Decision**: P10 is an operational cutover / dogfood / real-use readiness phase. Not a feature expansion phase. P10 prepares for P6 validation but must not claim it has started.
**Consequences**: P10 milestones focus on installation, real usage, friction discovery, and validation gating. No new product features during P10.
**Alternatives**: Start P6 validation immediately (rejected — no real usage data yet). Continue feature expansion (rejected — delays real use).
