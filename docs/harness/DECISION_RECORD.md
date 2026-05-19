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
