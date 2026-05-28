# Evidence Index

## Template

| Slice | Artifact | Path | Description |
|-------|----------|------|-------------|
| | | | |

## Evidence Log

| ALT-002 | Canonical snapshot.yaml | alters/current/snapshot.yaml | Phase 0 snapshot template with three anchors, intake_status, evidence_policy |
| ALT-002 | Intake workflow doc | docs/intake-workflow.md | One-question-at-a-time intake process, state machine, fallback prompts, hard prohibitions |
| ALT-002 | Quality gate update | docs/harness/QUALITY_GATES.md | Added Snapshot Intake quality gate with pass/fail criteria |
| ALT-003 | Canonical branches.yaml | alters/current/branches.yaml | Phase 0 branch discovery structure with pipeline, quality rules, branch template |
| ALT-003 | Branch discovery workflow | docs/branch-discovery-workflow.md | Three-step pipeline: tension extraction, structural branch identification, convergence |
| ALT-003 | Quality gate update | docs/harness/QUALITY_GATES.md | Added Branch Discovery quality gate with pass/fail criteria |
| ALT-003 | Task queue update | docs/harness/TASK_QUEUE.md | ALT-002 marked done, ALT-003 marked running |
| ALT-004 | Canonical alter template | alters/current/alters/_template.yaml | Inactive template with full alter structure: source_branch, life_state, personality_drift, tradeoffs, voice, value_alignment, quality_rules |
| ALT-004 | Alter generation workflow | docs/alter-generation-workflow.md | Four-step pipeline: structural commitment → life state, key tension → tradeoffs, rubric bias correction, voice generation. Valid/invalid criteria, hard prohibitions |
| ALT-004 | Quality gate update | docs/harness/QUALITY_GATES.md | Added Alter Generation quality gate with pass/fail criteria |
| ALT-004 | Branch discovery fix | docs/branch-discovery-workflow.md | Fixed intake_status "confirmed" → "completed" to match canonical snapshot |
| ALT-004 | Task queue update | docs/harness/TASK_QUEUE.md | ALT-003 marked done, ALT-004 marked done, ALT-005 marked blocked |
| ALT-005 | Canonical dialogue template | alters/current/dialogue/_template.yaml | Inactive template with dialogue structure: session, required_context, runtime_rules, messages, message_template, completion |
| ALT-005 | Dialogue engine workflow | docs/dialogue-engine-workflow.md | Eight-section workflow: purpose, input requirements, full injection rule, dialogue behavior, lifecycle, valid/invalid criteria, human confirmation, hard prohibitions |
| ALT-005 | Quality gate update | docs/harness/QUALITY_GATES.md | Added Dialogue Engine quality gate with pass/fail criteria |
| ALT-005 | Task queue update | docs/harness/TASK_QUEUE.md | ALT-005 marked running, ALT-006 marked blocked |
| ALT-005 | Task queue update | docs/harness/TASK_QUEUE.md | ALT-005 marked done, ALT-006 marked running, ALT-007 marked blocked |
| ALT-006 | Canonical value alignment template | alters/current/value_alignment/_template.yaml | Inactive template with value alignment structure: input_refs, value_profile, alignment_report, comparison, quality_rules |
| ALT-006 | Value alignment workflow | docs/value-alignment-workflow.md | Eight-section workflow: purpose, input requirements, value extraction, alignment dimensions, evaluation pipeline, valid/invalid criteria, human confirmation, hard prohibitions |
| ALT-006 | Quality gate update | docs/harness/QUALITY_GATES.md | Added Value Alignment Evaluator quality gate with pass/fail criteria |
| ALT-006 | Task queue update | docs/harness/TASK_QUEUE.md | ALT-005 marked done, ALT-006 marked running, ALT-007 marked blocked |
| ALT-007 | Normalized rubric | alters/calibration/rubric.yaml | Canonical structure: version, mode, status, purpose, 4 dimensions, drift_formula, evolution_policy with auto_modify: false |
| ALT-007 | Cold-start state | alters/calibration/state.json | Cold-start state with checkpoints_completed, current_drift, rubric_version tracking |
| ALT-007 | Score template | alters/calibration/scores/_template.yaml | Inactive template only with predicted/actual structure, drift computation, quality rules |
| ALT-007 | Calibration workflow | docs/calibration-system-workflow.md | Eight-section workflow: purpose, inputs, two-speed model, dimensions, cold-start policy, evolution policy, valid/invalid, hard prohibitions |
| ALT-007 | Quality gate update | docs/harness/QUALITY_GATES.md | Added Calibration + Rubric quality gate with pass/fail criteria |
| ALT-007 | Task queue update | docs/harness/TASK_QUEUE.md | ALT-006 marked done, ALT-007 marked running, ALT-008 marked blocked |
| ALT-007 | Project board update | docs/harness/PROJECT_BOARD.md | ALT-007 marked done, ALT-008 marked running |
| ALT-008 | Archive snapshot template | alters/archive/_template/snapshot.yaml | Inactive template with archive_id, snapshot structure, quality rules |
| ALT-008 | Archive branches template | alters/archive/_template/branches.yaml | Inactive template with archive_id, branch discovery structure, quality rules |
| ALT-008 | Archive alters .gitkeep | alters/archive/_template/alters/.gitkeep | Empty placeholder for archived alter files |
| ALT-008 | Archive reality trace template | alters/archive/_template/reality_trace.yaml | Inactive template with archive_id, events list, event_template, quality rules |
| ALT-008 | Archive reality score template | alters/archive/_template/reality_score.yaml | Inactive template with archive_id, per_branch scores, drift summary, quality rules |
| ALT-008 | Archive resolution template | alters/archive/_template/resolution.yaml | Inactive template with archive_id, resolution structure, quality rules |
| ALT-008 | Archive rubric delta template | alters/archive/_template/rubric_delta.yaml | Inactive template with archive_id, reject_auto_apply: true, quality rules |
| ALT-008 | Archive workflow doc | docs/archive-system-workflow.md | Nine-section workflow: purpose, inputs, naming, contents, triggers, process, valid/invalid, rubric delta policy, hard prohibitions |
| ALT-008 | Quality gate update | docs/harness/QUALITY_GATES.md | Added Archive System quality gate with pass/fail criteria and checklist items |
| ALT-008 | Task queue update | docs/harness/TASK_QUEUE.md | ALT-007 marked done, ALT-008 marked running |
| P0-CLOSEOUT | Final gate review | docs/harness/RUN_LOG.md | Phase 0 closeout entry appended. All 5 checks passed. |
| P0-CLOSEOUT | Decision record | docs/harness/DECISION_RECORD.md | P0-CLOSEOUT-01: Phase 0 workspace complete, ready for CYCLE-001A |
| P0-CLOSEOUT | Project board update | docs/harness/PROJECT_BOARD.md | ALT-008 marked done, CYCLE-001A added as ready-with-approval |
| P0-CLOSEOUT | Task queue update | docs/harness/TASK_QUEUE.md | ALT-008 marked done, CYCLE-001A added as ready-with-approval |
| P1-001 | pyproject.toml | apps/api/pyproject.toml | Minimal project config: fastapi, pydantic, pytest, uvicorn |
| P1-001 | FastAPI app | apps/api/src/alters_lab/main.py | FastAPI app with GET /health route returning status ok |
| P1-001 | Snapshot schemas | apps/api/src/alters_lab/schemas/snapshot.py | IntakePhase, AnchorName enums; Snapshot, SnapshotAnchors, SnapshotContext, SnapshotIntakeStatus, EvidencePolicy models with completion validation |
| P1-001 | Snapshot Intake service | apps/api/src/alters_lab/services/snapshot_intake.py | Pure functions: create_empty_snapshot, next_anchor, record_anchor_answer, ready_for_confirmation, mark_snapshot_completed |
| P1-001 | Schema tests | apps/api/tests/test_snapshot_schema.py | 4 tests: empty valid, completed valid, completed missing rejected, version < 1 rejected |
| P1-001 | Service tests | apps/api/tests/test_snapshot_intake.py | 9 tests: create empty, next anchor order, advance through anchors, ready confirmation, mark completed, empty rejected, no branch/alter artifacts |
| P1-001 | Task queue update | docs/harness/TASK_QUEUE.md | P1-001 done, P1-002 todo |
| P1-001 | Project board update | docs/harness/PROJECT_BOARD.md | Phase 1 section added, day_14 and day_30 gates, P1-001 done |
| P1-001 | Decision record | docs/harness/DECISION_RECORD.md | P1-001-01: Phase 1 starts with Snapshot Intake backend contract |
| P1-001 | Risk register update | docs/harness/RISK_REGISTER.md | R-007 through R-011 added for Phase 1 risks |
| P1-002 | In-memory session store | apps/api/src/alters_lab/services/snapshot_sessions.py | SnapshotSession class, InMemorySnapshotSessionStore with create/get/update/clear |
| P1-002 | API schemas | apps/api/src/alters_lab/schemas/snapshot.py | SnapshotSessionRead, AnchorAnswerRequest, NextAnchorResponse, SnapshotConfirmationResponse added |
| P1-002 | API router | apps/api/src/alters_lab/api/snapshot_intake.py | 6 endpoints: health, create session, get session, next anchor, submit answer, confirm snapshot |
| P1-002 | Updated main.py | apps/api/src/alters_lab/main.py | Snapshot intake router included |
| P1-002 | Updated pyproject.toml | apps/api/pyproject.toml | httpx added to dev dependencies for TestClient |
| P1-002 | API tests | apps/api/tests/test_snapshot_api.py | 20 tests: health, session CRUD, next anchor progression, answer validation, confirmation, YAML boundary checks |
| P1-002 | Task queue update | docs/harness/TASK_QUEUE.md | P1-002 marked done |
| P1-002 | Project board update | docs/harness/PROJECT_BOARD.md | P1-002 marked done, notes updated |
| P1-002 | Decision record | docs/harness/DECISION_RECORD.md | P1-002-01: in-memory API before file persistence |
| P1-002 | Risk register update | docs/harness/RISK_REGISTER.md | R-012 through R-016 added for API layer risks |
| P1-002 | Run log update | docs/harness/RUN_LOG.md | P1-002 entry appended |
| P1-003 | Snapshot export service | apps/api/src/alters_lab/services/snapshot_export.py | snapshot_to_canonical_dict, snapshot_to_yaml, write_snapshot_yaml functions for canonical YAML export |
| P1-003 | PyYAML dependency | apps/api/pyproject.toml | pyyaml added to dependencies for YAML serialization |
| P1-003 | Export tests | apps/api/tests/test_snapshot_export.py | 13 tests: canonical dict, YAML string, incomplete rejection, write to tmp_path, overwrite control, confirm boundary, no branch/alter artifacts |
| P1-003 | API README | apps/api/README.md | Created with endpoints, services, export, and run instructions |
| P1-003 | Task queue update | docs/harness/TASK_QUEUE.md | P1-003 marked done |
| P1-003 | Project board update | docs/harness/PROJECT_BOARD.md | P1-003 marked done |
| P1-003 | Decision record | docs/harness/DECISION_RECORD.md | P1-003-01: export path is service-only, not wired to confirm endpoint |
| P1-003 | Risk register update | docs/harness/RISK_REGISTER.md | R-017 and R-018 added for export path risks |
| P1-003 | Run log update | docs/harness/RUN_LOG.md | P1-003 entry appended |
| P2-001 | Loader models | apps/api/src/alters_lab/loaders/models.py | ActiveYamlPaths, ActiveYamlChain, ValidationResult dataclasses |
| P2-001 | Loader implementation | apps/api/src/alters_lab/loaders/active_yaml.py | default_project_root, active_yaml_paths, load_yaml_file, load_active_yaml_chain, validate_active_yaml_chain, summarize_active_yaml_chain |
| P2-001 | Loader package init | apps/api/src/alters_lab/loaders/__init__.py | Public API exports for loader package |
| P2-001 | Loader tests | apps/api/tests/test_active_yaml_loader.py | 11 tests: paths, load, validate, summarize, immutability, error cases |
| P2-001 | Project board update | docs/harness/PROJECT_BOARD.md | Phase 2 section added, P2-001 done, P2-002 blocked/todo |
| P2-001 | Task queue update | docs/harness/TASK_QUEUE.md | Phase 2 section added, P2-001 done, P2-002 blocked/todo |
| P2-001 | Decision record | docs/harness/DECISION_RECORD.md | P2-001-01: Phase 2 starts with read-only loaders |
| P2-001 | Risk register update | docs/harness/RISK_REGISTER.md | R-024 through R-028 added for Phase 2 loader risks |
| P2-001 | Run log update | docs/harness/RUN_LOG.md | P2-001 entry appended |
| P2-001 | Evidence index update | docs/harness/EVIDENCE_INDEX.md | P2-001 entry appended |
| P2-005R2 | Doc consistency patch | docs/harness/TASK_QUEUE.md, docs/harness/PHASE2_CLOSEOUT_REPORT.md, docs/harness/RUN_LOG.md, docs/harness/EVIDENCE_INDEX.md | Documentation-only consistency patch: P1-013 status updated, sealed commit corrected to fcfcbe2, test total corrected to 118, P2-005R slice recorded. No code changes. |
| P3-001R2 | Service rewrite | apps/api/src/alters_lab/services/snapshot_persist.py | Removed APPROVAL_TOKEN constant. Replaced persist_snapshot_to_disk with write_snapshot_with_audit. Added preview_snapshot_persist. Any non-empty token accepted. Audit stores hash only. Backup under configurable dir. |
| P3-001R2 | Schema repair | apps/api/src/alters_lab/schemas/snapshot.py | SnapshotPersistRequest model_validator rejects blank tokens. SnapshotPersistResponse exposes target_path/pre_write_hash/post_write_hash/audit_log_path/backup_path/governance_check/boundary_confirmations. No audit_record or would_write in response. |
| P3-001R2 | Endpoint repair | apps/api/src/alters_lab/api/snapshot_intake.py | Path helpers (target/audit/backup) monkeypatchable. Endpoint uses write_snapshot_with_audit. Boundary confirmations enumerate all 13 forbidden mutation surfaces. Dry_run returns status dry_run without write/audit. |
| P3-001R2 | Service tests | apps/api/tests/test_snapshot_persist.py | 27 tests: hash_approval_token exact hash, reject blank, no APPROVAL_TOKEN, governance pass/fail, preview no write/audit, write arbitrary token, canonical YAML, audit exact hash, no raw token, backup under dir, governance failure no write/audit, no forbidden files. |
| P3-001R2 | API tests | apps/api/tests/test_snapshot_persist_api.py | 19 tests: arbitrary token, reject blank/whitespace/missing, dry_run status/no write/no audit/no YAML, boundary confirmations, persist writes tmp only, audit tmp only, governance_check, boundary keys, no raw token in response/audit, exact hash, confirm no write, real snapshot unchanged, no forbidden routers. |
| P3-001R2 | Governance docs | docs/harness/PROJECT_BOARD.md, docs/harness/TASK_QUEUE.md, docs/harness/DECISION_RECORD.md, docs/harness/RISK_REGISTER.md, docs/harness/RUN_LOG.md, docs/harness/EVIDENCE_INDEX.md | P3-001R2 recorded. P3-002 blocked. Decision: approval tokens are evidence signals. Risks R-029 through R-033 added/mitigated. |
| P3-001R3 | Audit evidence cleanup | docs/harness/phase3_write_audit.jsonl | Removed stale old-schema audit log (12 entries with action/sha256_before/sha256_after from accidental test writes to alters/current/snapshot.yaml). No code changes. Active YAML unchanged. |
| P3-M1 | Shared controlled-write helpers | apps/api/src/alters_lab/services/controlled_write.py | sha256_text, sha256_file, hash_approval_token, reject_blank_token, safe_backup_path, append_jsonl_audit, create_backup_if_exists. Shared by branches and alters persist services. |
| P3-M1 | Branches schemas | apps/api/src/alters_lab/schemas/branches.py | BranchDiscoveryStatus, Branch, BranchDiscoveryPayload, BranchesPersistRequest (with to_payload), BranchesPersistResponse. |
| P3-M1 | Branches persist service | apps/api/src/alters_lab/services/branches_persist.py | branches_to_yaml, validate_branches_governance, preview_branches_persist, write_branches_with_audit. Governance enforces 4 branches, status completed, source_snapshot_ref correct, non-empty incompatible_with. |
| P3-M1 | Branches API router | apps/api/src/alters_lab/api/branches.py | GET /branches/health, POST /branches/persist. Monkeypatchable path helpers. |
| P3-M1 | Alter schemas | apps/api/src/alters_lab/schemas/alters.py | AlterSourceRefs, AlterQualityStatus, AlterVoice, AlterPayload (model_validator enforces id/branch_ref/source_refs/quality_status/voice), AlterPersistRequest, AlterBatchPersistRequest (validates all 4 alter IDs). |
| P3-M1 | Alter persist service | apps/api/src/alters_lab/services/alters_persist.py | alter_to_yaml, validate_alter_governance, validate_batch_governance, preview_alter_persist, write_alter_with_audit, write_alter_batch_with_audit. Batch is all-or-reject. |
| P3-M1 | Alter API router | apps/api/src/alters_lab/api/alters.py | GET /alters/health, POST /alters/persist/{alter_id}, POST /alters/persist-batch. Monkeypatchable path helpers. |
| P3-M1 | Branches service tests | apps/api/tests/test_branches_persist.py | 17 tests: governance valid/reject, preview no write/audit, write audit, backup, no forbidden files. |
| P3-M1 | Branches API tests | apps/api/tests/test_branches_persist_api.py | 15 tests: health, arbitrary token, reject blank/whitespace, dry_run status/write/audit/YAML/boundary, persist writes tmp, governance, boundary, no raw token, audit hash, no raw token in audit, reject incomplete, no generation routers. |
| P3-M1 | Alter service tests | apps/api/tests/test_alters_persist.py | 16 tests: governance valid/reject, batch all valid/reject invalid, preview, write audit, backup, no forbidden files, target path. |
| P3-M1 | Alter API tests | apps/api/tests/test_alters_persist_api.py | 16 tests: health, single persist arbitrary token, reject blank/whitespace, id mismatch, dry_run status/write/audit/boundary, persist writes tmp, governance, boundary, no raw token, audit hash, batch valid/invalid/dry_run, no generation routers. |
| P3-M1 | main.py update | apps/api/src/alters_lab/main.py | Added branches_router and alters_router includes. |
| P3-M1 | snapshot API test update | apps/api/tests/test_snapshot_persist_api.py | test_no_forbidden_routers: removed 'branch' and 'alter' from forbidden list (now valid controlled write routes). |
| P3-M1 | Governance docs | docs/harness/PROJECT_BOARD.md, docs/harness/TASK_QUEUE.md, docs/harness/RUN_LOG.md, docs/harness/EVIDENCE_INDEX.md | P3-002, P3-003, P3-M1 recorded as done. |
| P3-M1R | Branches schema hardening | apps/api/src/alters_lab/schemas/branches.py | Added ConfigDict(extra="forbid") to BranchDiscoveryStatus, Branch, BranchDiscoveryPayload, BranchesPersistRequest. |
| P3-M1R | Alters schema hardening | apps/api/src/alters_lab/schemas/alters.py | Added ConfigDict(extra="forbid") to AlterSourceRefs, AlterQualityStatus, AlterVoice, AlterPayload, AlterPersistRequest, AlterBatchPersistRequest. |
| P3-M1R | Health endpoint update | apps/api/src/alters_lab/api/branches.py, apps/api/src/alters_lab/api/alters.py | Both health endpoints now return mode: "controlled_write". |
| P3-M1R | Branches smuggling tests | apps/api/tests/test_branches_persist_api.py | 7 tests: top-level calibration/archive/provider/dialogue/runtime rejected, nested branch_discovery extra field rejected, nested branch item extra field rejected. |
| P3-M1R | Alters smuggling tests | apps/api/tests/test_alters_persist_api.py | 10 tests: top-level provider/dialogue/archive/database/frontend/generation/calibration_scoring/drift rejected, nested voice extra field rejected, batch alter with extra field rejected. |
| P3-M1R | Branches schema defense tests | apps/api/tests/test_branches_persist.py | 4 tests documenting schema-level extra="forbid" as first defense for BranchDiscoveryStatus, Branch, BranchDiscoveryPayload, BranchesPersistRequest. |
| P3-M1R | Alters schema defense tests | apps/api/tests/test_alters_persist.py | 4 tests documenting schema-level extra="forbid" as first defense for AlterSourceRefs, AlterPayload, AlterPersistRequest, AlterBatchPersistRequest. |
| P3-M1R | Governance docs | docs/harness/PROJECT_BOARD.md, docs/harness/TASK_QUEUE.md, docs/harness/DECISION_RECORD.md, docs/harness/RISK_REGISTER.md, docs/harness/RUN_LOG.md, docs/harness/EVIDENCE_INDEX.md | P3-M1R recorded. P3-M2 blocked. Decision P3-M1R-01 added. Risks R-038 (mitigated), R-039 (active) added. |
| P3-M2 | Generation draft schemas | apps/api/src/alters_lab/schemas/generation_drafts.py | 10 Pydantic models with ConfigDict(extra="forbid"): GenerationSourceRefs, GenerationBoundaryConfirmations, DraftGeneratorInfo, BranchDraftCandidate, AlterDraftCandidate, GenerationDraftPackage, GenerationPreviewRequest, GenerationPreviewResponse, DraftListResponse. |
| P3-M2 | Generation draft service | apps/api/src/alters_lab/services/generation_drafts.py | generate_draft_id, generation_boundary_confirmations, validate_generation_inputs, generate_branch_drafts_from_snapshot, generate_alter_drafts_from_branches, build_generation_draft_package, save_generation_draft_package, preview_generation_draft, list_generation_drafts. |
| P3-M2 | Generation draft API | apps/api/src/alters_lab/api/generation_drafts.py | GET /generation-drafts/health, POST /generation-drafts/preview, GET /generation-drafts/list. Monkeypatchable path helpers. |
| P3-M2 | main.py update | apps/api/src/alters_lab/main.py | Added generation_drafts_router include. |
| P3-M2 | Generation draft service tests | apps/api/tests/test_generation_drafts.py | 28 tests: boundary confirmations, validation, branch/alter draft generation, draft package, preview, save, list, extra field rejection. |
| P3-M2 | Generation draft API tests | apps/api/tests/test_generation_drafts_api.py | 17 tests: health, preview no save, preview with save, list, extra field rejection, active YAML unchanged, no forbidden routers, no provider imports. |
| P3-M2 | .gitignore update | .gitignore | Added alters/drafts/ and docs/harness/phase3_generation_draft_audit.jsonl. |
| P3-M2 | Governance docs | docs/harness/PROJECT_BOARD.md, docs/harness/TASK_QUEUE.md, docs/harness/DECISION_RECORD.md, docs/harness/RISK_REGISTER.md, docs/harness/RUN_LOG.md, docs/harness/EVIDENCE_INDEX.md | P3-M2 recorded. P3-M3 blocked pending human review. Decision P3-M2-01 added. Risks R-040 through R-043 added. |
| P3-M2R | Normalization helpers | apps/api/src/alters_lab/services/generation_drafts.py | Added normalize_active_chain (ActiveYamlChain | dict | None -> dict), extract_snapshot_body (wrapped/unwrapped), extract_branch_list. |
| P3-M2R | Service type hints | apps/api/src/alters_lab/services/generation_drafts.py | Updated validate_generation_inputs, build_generation_draft_package, preview_generation_draft to accept ActiveYamlChain | dict | None. |
| P3-M2R | API error handling | apps/api/src/alters_lab/api/generation_drafts.py | Loader failure returns HTTP 500, validation failure returns HTTP 400. No draft/audit on validation failure. |
| P3-M2R | Service normalization tests | apps/api/tests/test_generation_drafts.py | 14 tests: normalize_active_chain (4), extract_snapshot_body (3), extract_branch_list (2), real wrapped snapshot validation (2), dataclass build (2), unwrapped dict build (1). |
| P3-M2R | API real loader tests | apps/api/tests/test_generation_drafts_api.py | 3 tests: real loader without monkeypatch, real wrapped snapshot shape verification, validation failure 400, loader failure 500. |
| P3-M2R | Governance docs | docs/harness/PROJECT_BOARD.md, docs/harness/TASK_QUEUE.md, docs/harness/DECISION_RECORD.md, docs/harness/RISK_REGISTER.md, docs/harness/RUN_LOG.md, docs/harness/EVIDENCE_INDEX.md | P3-M2R recorded. P3-M2 updated to repaired_by_P3-M2R. Decision P3-M2R-01 added. |
| P3-M3 | Draft review schemas | apps/api/src/alters_lab/schemas/draft_review.py | 8 Pydantic models with ConfigDict(extra="forbid"): DraftReviewBoundaryConfirmations, DraftReviewDecision, DraftReviewRequest, PromotionBranchesPayload, PromotionAltersPayload, PromotionPackage, DraftReviewResponse, DraftReviewListResponse. |
| P3-M3 | Draft review service | apps/api/src/alters_lab/services/draft_review.py | draft_review_boundary_confirmations, load_draft_package, validate_draft_package_for_review, create_review_decision, build_branches_promotion_payload, build_alters_promotion_payload, build_promotion_package, save_review_decision, save_promotion_package, list_draft_reviews. |
| P3-M3 | Draft review API | apps/api/src/alters_lab/api/draft_review.py | GET /draft-review/health, POST /draft-review/{draft_id}/review, GET /draft-review/list. Monkeypatchable workspace helper. |
| P3-M3 | main.py update | apps/api/src/alters_lab/main.py | Added draft_review_router include. |
| P3-M3 | Draft review service tests | apps/api/tests/test_draft_review.py | 33 tests: boundary confirmations, load/reject/path-traversal, validate pass/reject (6), create decision (5), build payloads (4), build promotion package (3), save review/promotion (6), list (2), extra field rejection (2). |
| P3-M3 | Draft review API tests | apps/api/tests/test_draft_review_api.py | 16 tests: health, 404 missing, path traversal, preview no-write, approve promotion, save files, save requires token, no active YAML, no raw token, list empty/metadata, extra field rejection (2), no forbidden routers, no provider imports, no persist API calls. |
| P3-M3 | Governance docs | docs/harness/PROJECT_BOARD.md, docs/harness/TASK_QUEUE.md, docs/harness/DECISION_RECORD.md, docs/harness/RISK_REGISTER.md, docs/harness/RUN_LOG.md, docs/harness/EVIDENCE_INDEX.md | P3-M3 recorded. Decision P3-M3-01 added. Risks R-047 through R-050 added. |
| P3-M3R | Schema guard validators | apps/api/src/alters_lab/schemas/draft_review.py | PromotionPackage model_validator: active_write_allowed must be false, requires_controlled_persist_api must be true, target_persist_apis restricted. |
| P3-M3R | Service validation hardening | apps/api/src/alters_lab/services/draft_review.py | validate_draft_package_for_review: complete branch_A-D/alter_A-D, branch_ref, voice.core_stance, incompatible_with. build_alters_promotion_payload: branch_ref, voice, source_refs validation. |
| P3-M3R2 | Exactness repair | apps/api/src/alters_lab/services/draft_review.py | count==4, duplicate ID detection, source_refs compatibility for alter drafts. build_branches/alters_promotion_payload: exactly 4 unique items after filtering. |
| P3-M4 | Promotion orchestration schemas | apps/api/src/alters_lab/schemas/promotion_orchestration.py | 8 Pydantic models with ConfigDict(extra="forbid"): PromotionOrchestrationBoundaryConfirmations, PromotionPlanStep, PromotionEvidenceRequirement, PromotionRollbackPlan, PromotionOrchestrationPlan, PromotionOrchestrationRequest, PromotionOrchestrationResponse, PromotionOrchestrationListResponse. |
| P3-M4 | Promotion orchestration service | apps/api/src/alters_lab/services/promotion_orchestration.py | promotion_orchestration_boundary_confirmations, validate_draft_id, load_promotion_package, validate_promotion_package_for_orchestration, build_promotion_steps, build_evidence_requirements, build_rollback_plan, build_orchestration_plan, save_orchestration_plan, list_orchestration_plans. |
| P3-M4 | Promotion orchestration API | apps/api/src/alters_lab/api/promotion_orchestration.py | GET /promotion-orchestration/health, POST /promotion-orchestration/{draft_id}/plan, GET /promotion-orchestration/list. Monkeypatchable workspace helper. |
| P3-M4 | main.py update | apps/api/src/alters_lab/main.py | Added promotion_orchestration_router include. |
| P3-M4 | Service tests | apps/api/tests/test_promotion_orchestration.py | 33 tests: boundary confirmations, validate_draft_id (4), load/reject/path-traversal (3), validate pass/reject (13), build steps/evidence/rollback (6), build orchestration plan (2), save/reject/no-raw-token (3), list (2), extra field rejection (2). |
| P3-M4 | API tests | apps/api/tests/test_promotion_orchestration_api.py | 21 tests: health, 404 missing, path traversal, plan no-write, plan active_execution_false, plan steps allowed APIs, save requires token, save writes file, no raw token in response/file, no active YAML, list empty/metadata, extra field rejection (2), no forbidden routers, no provider imports, no persist API calls, route inventory. |
| P3-M4 | Governance docs | docs/harness/PROJECT_BOARD.md, docs/harness/TASK_QUEUE.md, docs/harness/DECISION_RECORD.md, docs/harness/RISK_REGISTER.md, docs/harness/RUN_LOG.md, docs/harness/EVIDENCE_INDEX.md | P3-M4 recorded. P3-M5 blocked. Decision P3-M4-01 added. Risks R-051 through R-056 added. |
| P3-M5 | Execution gate schemas | apps/api/src/alters_lab/schemas/promotion_execution_gate.py | 8 Pydantic models with ConfigDict(extra="forbid"): PromotionExecutionGateBoundaryConfirmations, ExecutionPrerequisiteCheck, DryRunCheckResult, ExecutionPacket, PromotionExecutionGateReport, PromotionExecutionGateRequest, PromotionExecutionGateResponse, PromotionExecutionGateListResponse. |
| P3-M5 | Execution gate service | apps/api/src/alters_lab/services/promotion_execution_gate.py | promotion_execution_gate_boundary_confirmations, validate_draft_id, load_gate_inputs, validate_orchestration_plan_for_execution_gate, validate_promotion_package_for_execution_gate, compare_package_and_plan, build_prerequisite_checks, run_dry_run_compatibility_checks, build_execution_packet, build_gate_report, save_gate_report, list_execution_gate_reports. |
| P3-M5 | Execution gate API | apps/api/src/alters_lab/api/promotion_execution_gate.py | GET /promotion-execution-gate/health, POST /promotion-execution-gate/{draft_id}/check, GET /promotion-execution-gate/list. Monkeypatchable workspace helper. |
| P3-M5 | main.py update | apps/api/src/alters_lab/main.py | Added promotion_execution_gate_router include. |
| P3-M5 | Service tests | apps/api/tests/test_promotion_execution_gate.py | 38 tests: boundary confirmations, validate_draft_id (4), load_gate_inputs (4), validate plan (7), validate package (6), compare (5), prerequisites (2), dry_run (3), packet (2), gate_report (3), save (3), list (2), extra field rejection (2). |
| P3-M5 | API tests | apps/api/tests/test_promotion_execution_gate_api.py | 21 tests: health, 404 missing, path traversal, check no-write, check gate_passed, check fails without token, save requires token, save writes files, no raw token in response/file, no active YAML, dry_run_only, list empty/metadata, extra field rejection (2), no forbidden routers, no provider imports, no persist API calls, route inventory. |
| P3-M5 | Governance docs | docs/harness/PROJECT_BOARD.md, docs/harness/TASK_QUEUE.md, docs/harness/DECISION_RECORD.md, docs/harness/RISK_REGISTER.md, docs/harness/RUN_LOG.md, docs/harness/EVIDENCE_INDEX.md | P3-M5 recorded. Decision P3-M5-01 added. Risks R-057 through R-062 added. |
| P3-M6 | Live execution schemas | apps/api/src/alters_lab/schemas/promotion_live_execution.py | 6 Pydantic models with ConfigDict(extra="forbid"): PromotionLiveExecutionBoundaryConfirmations, LiveExecutionStepResult, PromotionLiveExecutionReport, PromotionLiveExecutionRequest, PromotionLiveExecutionResponse, PromotionLiveExecutionListResponse. |
| P3-M6 | Live execution service | apps/api/src/alters_lab/services/promotion_live_execution.py | promotion_live_execution_boundary_confirmations, validate_draft_id, load_live_execution_inputs, validate_gate_for_live_execution, extract_branches_persist_payload, extract_alters_persist_payload, execute_promotion_dry_run, execute_promotion_live, build_live_execution_report, run_live_execution_gate, save_live_execution_report, list_live_execution_reports. |
| P3-M6 | Live execution API | apps/api/src/alters_lab/api/promotion_live_execution.py | GET /promotion-live-execution/health, POST /promotion-live-execution/{draft_id}/run, GET /promotion-live-execution/list. Monkeypatchable workspace helper. LIVE_EXECUTION_ENABLED flag. |
| P3-M6 | main.py update | apps/api/src/alters_lab/main.py | Added promotion_live_execution_router include. |
| P3-M6 | Service tests | apps/api/tests/test_promotion_live_execution.py | 31 tests: boundary confirmations, validate_draft_id (4), load inputs (3), validate gate (9), extract branches (5), extract alters (5), build report (3), save report (3), list (2), run gate (4), extra field rejection (3). |
| P3-M6 | API tests | apps/api/tests/test_promotion_live_execution_api.py | 32 tests: health, dry_run missing/404, dry_run passes, dry_run rejected without token, dry_run save writes file, dry_run no raw token, dry_run no active YAML, live rejected when not enabled, live rejected without path_overrides, live requires token, save requires token, invalid mode, list empty/metadata, extra field rejection (2), no forbidden routers, no provider imports, route inventory. |
| P3-M6 | Governance docs | docs/harness/PROJECT_BOARD.md, docs/harness/TASK_QUEUE.md, docs/harness/DECISION_RECORD.md, docs/harness/RISK_REGISTER.md, docs/harness/RUN_LOG.md, docs/harness/EVIDENCE_INDEX.md | P3-M6 recorded. Decision P3-M6-01 added. |
| P3-M6R | Service fix | apps/api/src/alters_lab/services/promotion_live_execution.py | Fixed execute_promotion_live() kwargs for controlled persist services. Added BranchDiscoveryPayload/AlterPayload model conversions. Fixed batch alters hash handling. |
| P3-M6R | Schema fix | apps/api/src/alters_lab/schemas/alters.py, apps/api/src/alters_lab/schemas/branches.py | Changed AlterPayload, BranchDiscoveryPayload, BranchDiscoveryStatus from extra="forbid" to extra="allow". |
| P3-M6R | Test updates | apps/api/tests/test_alters_persist.py, apps/api/tests/test_alters_persist_api.py, apps/api/tests/test_branches_persist.py, apps/api/tests/test_branches_persist_api.py, apps/api/tests/test_promotion_live_execution.py, apps/api/tests/test_promotion_live_execution_api.py | 6 tests updated for new extra="allow" behavior and complete test data. |
| P3-M7 | Live promotion evidence | docs/harness/P3_M7_LIVE_PROMOTION_EVIDENCE.json | Semantic no-op live promotion run evidence. Baseline and post-live hashes identical. 568 tests pass. Active chain validation pass. |
| P3-M7 | Governance docs | docs/harness/PROJECT_BOARD.md, docs/harness/TASK_QUEUE.md, docs/harness/DECISION_RECORD.md, docs/harness/RUN_LOG.md, docs/harness/EVIDENCE_INDEX.md | P3-M6R and P3-M7 recorded. Decisions P3-M6R-01 and P3-M7-01 added. |
| P3-M6R2 | Schema revert | apps/api/src/alters_lab/schemas/alters.py, apps/api/src/alters_lab/schemas/branches.py | Reverted AlterPayload, BranchDiscoveryPayload, BranchDiscoveryStatus to extra="forbid". Supersedes P3-M6R-01. |
| P3-M6R2 | Raw dict write functions | apps/api/src/alters_lab/services/alters_persist.py, apps/api/src/alters_lab/services/branches_persist.py | Added validate_alter_raw_dict, write_alter_raw_batch_with_audit, write_branches_raw_with_audit. Raw dict round-trip preserves all YAML extras without Pydantic model_dump() stripping. |
| P3-M6R2 | Live execution update | apps/api/src/alters_lab/services/promotion_live_execution.py | execute_promotion_live now uses write_branches_raw_with_audit and write_alter_raw_batch_with_audit instead of Pydantic model path. |
| P3-M6R2 | Tests | apps/api/tests/test_alters_persist.py, apps/api/tests/test_branches_persist.py, apps/api/tests/test_promotion_live_execution.py | 8 new tests: raw dict validation (5), raw dict write preserving extras (3). Mock targets updated. 576 tests passing. |
| P3-M6R2 | Governance docs | docs/harness/DECISION_RECORD.md, docs/harness/RUN_LOG.md, docs/harness/EVIDENCE_INDEX.md | Decision P3-M6R2-01 added. P3-M6R-01 superseded. P3-M6R2 recorded. |
| P3-M8 | Closeout schemas | apps/api/src/alters_lab/schemas/phase3_closeout.py | 6 Pydantic models with ConfigDict(extra="forbid"): Phase3CloseoutBoundaryConfirmations, Phase3CloseoutCheck, Phase3CloseoutSummary, Phase3CloseoutReport, Phase3CloseoutResponse, Phase3CloseoutEvidenceResponse. |
| P3-M8 | Closeout service | apps/api/src/alters_lab/services/phase3_closeout.py | 9 verification checks: active_yaml_chain, phase3_evidence_files, p3_m7_semantic_noop_evidence, smuggling_boundary_restored, raw_dict_repersist_path_exists, live_execution_default_safe, no_runtime_artifacts_committed, no_raw_audit_logs_committed, phase3_governance_status. build_phase3_closeout_report, write_phase3_closeout_artifacts. |
| P3-M8 | Closeout API | apps/api/src/alters_lab/api/phase3_closeout.py | GET /phase3-closeout/health, GET /phase3-closeout/report, GET /phase3-closeout/evidence. Read-only endpoints. |
| P3-M8 | Service tests | apps/api/tests/test_phase3_closeout.py | 17 tests: boundary confirmations, repo root, 9 individual checks, build report, write artifacts, content verification, schema defense. |
| P3-M8 | API tests | apps/api/tests/test_phase3_closeout_api.py | 13 tests: health, report returns, report no-write, report checks, evidence 404/evidence found, no mutation routes, route inventory, no active YAML written, extra field rejection. |
| P3-M8 | Governance docs | docs/harness/PROJECT_BOARD.md, docs/harness/TASK_QUEUE.md, docs/harness/DECISION_RECORD.md, docs/harness/RUN_LOG.md, docs/harness/EVIDENCE_INDEX.md | P3-M8 recorded. Decision P3-M8-01 added. P4-000 blocked. |
| P3-M8R2 | Closeout service fix | apps/api/src/alters_lab/services/phase3_closeout.py | Updated check_no_raw_audit_logs_committed to use git ls-files for tracking check. Updated check_no_runtime_artifacts_committed with same git-aware logic. FAIL for tracked, WARN for untracked/ignored. |
| P3-M8R2 | Test updates | apps/api/tests/test_phase3_closeout.py | Added test_check_no_raw_audit_logs_with_local_audit (WARN) and test_check_no_raw_audit_logs_with_tracked_audit (FAIL). Renamed test_check_no_raw_audit_logs_with_audit to avoid conflict. |
| P3-M8R2 | Closeout artifacts | docs/harness/PHASE3_CLOSEOUT_REPORT.md, docs/harness/PHASE3_CLOSEOUT_EVIDENCE.json | Phase 3 closeout PASS_WITH_NOTES. Sealed baseline candidate True. Baseline commit 86b75aa. 607 tests. |
| P3-M8R2 | Governance docs | docs/harness/PROJECT_BOARD.md, docs/harness/TASK_QUEUE.md, docs/harness/DECISION_RECORD.md, docs/harness/RISK_REGISTER.md, docs/harness/RUN_LOG.md, docs/harness/EVIDENCE_INDEX.md | P3-M8R2 recorded. Decision P3-M8R2-01 added. Risks R-063, R-064 added. Phase 3 sealed baseline established. |
| P4-000 | Scope plan | docs/harness/P4_000_PHASE4_SCOPE_AND_BOUNDARY_PLAN.md | Phase 4 scope and boundary plan. 7 milestones, semantic mutation policy, promotion/approval/rollback/audit models. |
| P4-000 | Governance docs | docs/harness/PROJECT_BOARD.md, docs/harness/TASK_QUEUE.md, docs/harness/DECISION_RECORD.md, docs/harness/RISK_REGISTER.md, docs/harness/RUN_LOG.md, docs/harness/EVIDENCE_INDEX.md | P4-000 recorded. Decisions P4-000-01, P4-000-02 added. Risks R-065 through R-069 added. P4-M1 blocked. |
| P4-M1 | Alter dialogue schemas | apps/api/src/alters_lab/schemas/alter_dialogue.py | 7 Pydantic models with ConfigDict(extra="forbid"): AlterDialogueBoundaryConfirmations, AlterDialogueContext, AlterDialogueRequest, AlterDialoguePromptPacket, AlterDialogueResponse, AlterDialogueHealthResponse, AlterDialogueListResponse. |
| P4-M1 | Alter dialogue service | apps/api/src/alters_lab/services/alter_dialogue.py | alter_dialogue_boundary_confirmations, validate_alter_id, load_active_alter, validate_active_alter_for_dialogue, build_alter_dialogue_context, build_system_instruction, build_prompt_packet, list_active_alters, build_dialogue_response. Read-only, no provider, no writes. |
| P4-M1 | Alter dialogue API | apps/api/src/alters_lab/api/alter_dialogue.py | GET /alter-dialogue/health, GET /alter-dialogue/alters, GET /alter-dialogue/{alter_id}/context, POST /alter-dialogue/{alter_id}/prompt. Read-only endpoints. |
| P4-M1 | main.py update | apps/api/src/alters_lab/main.py | Added alter_dialogue_router include. |
| P4-M1 | Service tests | apps/api/tests/test_alter_dialogue.py | 28 tests: boundary confirmations, validate_alter_id (4), get_repo_root, load_active_alter (2), validate_active_alter (7), build_context, build_system_instruction, build_prompt_packet (2), list_active_alters (2), build_dialogue_response (3), request validation (2), schema defense (1). |
| P4-M1 | API tests | apps/api/tests/test_alter_dialogue_api.py | 21 tests: health, list_alters (2), get_context (3), prompt (3), prompt rejects (5), route inventory, no active YAML written, no provider imports, no persist/live calls, prompt no-write. |
| P4-M1 | Test fixes | tests/test_alters_persist_api.py, tests/test_branches_persist_api.py, tests/test_snapshot_persist_api.py, tests/test_draft_review_api.py, tests/test_generation_drafts_api.py, tests/test_promotion_execution_gate_api.py, tests/test_promotion_live_execution_api.py, tests/test_promotion_orchestration_api.py | Updated forbidden route checks to exclude /alter-dialogue (P4-M1 approved read-only dialogue runtime). |
| P4-M1 | Governance docs | docs/harness/PROJECT_BOARD.md, docs/harness/TASK_QUEUE.md, docs/harness/DECISION_RECORD.md, docs/harness/RISK_REGISTER.md, docs/harness/RUN_LOG.md, docs/harness/EVIDENCE_INDEX.md | P4-M1 recorded. Decision P4-M1-01 added. Risks R-070 through R-074 added. P4-M2 blocked. |
| P4-CAL-LOOP-MVP | Dialogue contract hardening | apps/api/src/alters_lab/schemas/alter_dialogue.py, apps/api/src/alters_lab/services/alter_dialogue.py | P4-M1R: AlterDialoguePromptPacket now includes full_alter_yaml, full_context_injected, and context_injection_policy=full_alter_yaml_required. |
| P4-CAL-LOOP-MVP | Calibration loop schemas | apps/api/src/alters_lab/schemas/calibration_loop.py | P4-M2/M3/M4 schemas for explicit reality scores, score values, drift calculation result, history response, and boundary confirmations; all use ConfigDict(extra="forbid"). |
| P4-CAL-LOOP-MVP | Calibration loop service | apps/api/src/alters_lab/services/calibration_loop.py | Explicit user score record writer under alters/calibration/scores, evidence-only drift calculation, read-only history listing with derived drift. |
| P4-CAL-LOOP-MVP | Calibration loop API | apps/api/src/alters_lab/api/calibration_loop.py, apps/api/src/alters_lab/main.py | GET /calibration-loop/health, POST /calibration-loop/reality-scores, POST /calibration-loop/drift/calculate, GET /calibration-loop/history; router registered in FastAPI. |
| P4-CAL-LOOP-MVP | Tests | apps/api/tests/test_calibration_loop.py, apps/api/tests/test_calibration_loop_api.py, apps/api/tests/test_alter_dialogue.py, apps/api/tests/test_alter_dialogue_api.py | Service/API coverage for explicit score submission, schema smuggling rejection, no active YAML/rubric writes, evidence-only drift, read-only history, full alter YAML prompt packets. |
| P4-CAL-LOOP-MVP | Governance docs and evidence | apps/api/README.md, docs/calibration-system-workflow.md, docs/harness/QUALITY_GATES.md, docs/harness/PROJECT_BOARD.md, docs/harness/DECISION_RECORD.md, docs/harness/RISK_REGISTER.md, docs/harness/RUN_LOG.md, docs/harness/P4_CAL_LOOP_MVP_EVIDENCE.json | P4-M1R/P4-M2/P4-M3/P4-M4 recorded without modifying TASK_QUEUE.md, alters/current/**, or rubric.yaml. |
| P4-FINAL | Rubric Delta Suggestion | apps/api/src/alters_lab/schemas/rubric_delta.py, apps/api/src/alters_lab/services/rubric_delta.py, apps/api/src/alters_lab/api/rubric_delta.py | P4-M5 suggestion-only rubric delta detection. Optional save writes only under alters/calibration/rubric_delta_suggestions/. |
| P4-FINAL | Archive Mechanism | apps/api/src/alters_lab/schemas/archive_mechanism.py, apps/api/src/alters_lab/services/archive_mechanism.py, apps/api/src/alters_lab/api/archive_mechanism.py | P4-M6 explicit-only archive planning and copy-only archive creation under alters/archive/checkpoints/. |
| P4-FINAL | Checkpoint Regeneration Plan | apps/api/src/alters_lab/schemas/checkpoint_regeneration.py, apps/api/src/alters_lab/services/checkpoint_regeneration.py, apps/api/src/alters_lab/api/checkpoint_regeneration.py | P4-M7 plan-only high-drift checkpoint review plans. No active regeneration. |
| P4-FINAL | Phase 4 Closeout | apps/api/src/alters_lab/schemas/phase4_closeout.py, apps/api/src/alters_lab/services/phase4_closeout.py, apps/api/src/alters_lab/api/phase4_closeout.py, docs/harness/PHASE4_CLOSEOUT_REPORT.md, docs/harness/PHASE4_CLOSEOUT_EVIDENCE.json, docs/harness/P4_FINAL_EVIDENCE.json | Closeout verifies P4-M1R through P4-M7, no active YAML/rubric diff, no provider/frontend/database, no committed raw runtime records. |
| P5-FULL | P5-000 Boundary Plan | docs/harness/P5_000_PRODUCTIZATION_PROVIDER_FRONTEND_BOUNDARY_PLAN.md | P5 identity, provider modes, frontend scope, storage scope, active YAML safety, dialogue safety, persistent writes, forbidden items, exit gate, module inventory. |
| P5-FULL | Product Surface schemas | apps/api/src/alters_lab/schemas/product_surface.py | 5 models: ProductHealthResponse, RouteClassification, ProductRoutesResponse, ProductStatusResponse, ProductWorkflowCapabilitiesResponse. |
| P5-FULL | Product Surface service | apps/api/src/alters_lab/services/product_surface.py | Route classification (safe/internal/dangerous), product status summary, workflow capabilities inventory. Read-only. |
| P5-FULL | Product Surface API | apps/api/src/alters_lab/api/product_surface.py | GET /product/health, /routes, /status, /workflow-capabilities. |
| P5-FULL | Provider Gateway schemas | apps/api/src/alters_lab/schemas/provider_gateway.py | 4 models: ProviderGatewayRequest, ProviderGatewayResponse, ProviderGatewayHealthResponse, ProviderConfigStatusResponse. |
| P5-FULL | Provider Gateway service | apps/api/src/alters_lab/services/provider_gateway.py | Mock/disabled/openai_compatible_http modes. Secret redaction. No SDK imports. |
| P5-FULL | Provider Gateway API | apps/api/src/alters_lab/api/provider_gateway.py | GET /provider-gateway/health, /config-status; POST /provider-gateway/complete. |
| P5-FULL | Provider Dialogue schemas | apps/api/src/alters_lab/schemas/provider_dialogue.py | 4 models: ProviderDialogueBoundaryConfirmations, ProviderDialogueReplyRequest, ProviderDialogueReplyResponse, ProviderDialogueHealthResponse. |
| P5-FULL | Provider Dialogue service | apps/api/src/alters_lab/services/provider_dialogue.py | Full alter YAML prompt packet. save_session defaults to false. Sessions to alters/product/sessions/. |
| P5-FULL | Provider Dialogue API | apps/api/src/alters_lab/api/provider_dialogue.py | GET /provider-dialogue/health; POST /provider-dialogue/{alter_id}/reply. |
| P5-FULL | Storage Boundary schemas | apps/api/src/alters_lab/schemas/storage_boundary.py | 3 models: StoragePathClassification, StorageManifestResponse, StorageBoundaryHealthResponse. |
| P5-FULL | Storage Boundary service | apps/api/src/alters_lab/services/storage_boundary.py | YAML default. Path classification: active read-only, score write, product session write, ignored runtime, evidence. |
| P5-FULL | Storage Boundary API | apps/api/src/alters_lab/api/storage_boundary.py | GET /storage-boundary/health, /manifest. |
| P5-FULL | User Workflow schemas | apps/api/src/alters_lab/schemas/user_workflow.py | 4 models: UserWorkflowStateResponse, WorkflowRunSummaryRequest, WorkflowRunSummaryResponse, UserWorkflowHealthResponse. |
| P5-FULL | User Workflow service | apps/api/src/alters_lab/services/user_workflow.py | Workflow state (alters, provider, scores, drift, rubric delta, checkpoint plan). Run summary to alters/product/workflow_runs/. |
| P5-FULL | User Workflow API | apps/api/src/alters_lab/api/user_workflow.py | GET /user-workflow/health, /state; POST /user-workflow/run-summary. |
| P5-FULL | Phase 5 Closeout schemas | apps/api/src/alters_lab/schemas/phase5_closeout.py | 5 models: CloseoutCheck, CloseoutSummary, Phase5CloseoutReportResponse, Phase5CloseoutEvidenceResponse, Phase5CloseoutHealthResponse. |
| P5-FULL | Phase 5 Closeout service | apps/api/src/alters_lab/services/phase5_closeout.py | 9 verification checks. Generates PHASE5_CLOSEOUT_EVIDENCE.json and P5_FINAL_EVIDENCE.json. |
| P5-FULL | Phase 5 Closeout API | apps/api/src/alters_lab/api/phase5_closeout.py | GET /phase5-closeout/health, /report, /evidence. |
| P5-FULL | Frontend MVP | apps/web/ | Vite + React + TypeScript. 6 pages: SystemStatus, AlterDialogue, RealityScore, CalibrationHistory, RubricDelta, CheckpointPlan. |
| P5-FULL | Tests (backend) | apps/api/tests/test_product_surface*.py, test_provider_gateway*.py, test_provider_dialogue*.py, test_storage_boundary*.py, test_user_workflow*.py, test_phase5_closeout*.py | 73 new tests. All 802 tests passing. |
| P5-FULL | Local Release Candidate | docs/harness/P5_LOCAL_RELEASE_CANDIDATE.md | Backend/frontend start commands, provider explanation, demo workflow, safety notes, route inventory. |
| P5-FULL | Governance updates | docs/harness/PROJECT_BOARD.md, TASK_QUEUE.md, DECISION_RECORD.md, RISK_REGISTER.md, RUN_LOG.md, EVIDENCE_INDEX.md | P5 milestones recorded. 7 decisions (P5-000-01 through P5-M7-01). 7 risks (R-085 through R-091). |
| P6-000 | Personal long-term use hardening plan | docs/harness/P6_000_PERSONAL_LONG_TERM_USE_HARDENING_PLAN.md | P6 plan with 30 core decisions, 11 milestones (P6-M1 through P6-M11), usage cadence, scoring model, self-deception tracking, alter challenge mode, evidence source policy, 4-week validation window. |
| P6-000 | P6 decision ledger | docs/harness/P6_DECISION_LEDGER.md | 8 ledger entries (P6-DL-01 through P6-DL-08) covering: personal use over productization, behavior change as success, Obsidian raw note as evidence, action alignment as metric, dual-layer output, 4-week validation, provider default disabled, no-improvement usage integrity audit. |
| P6-000 | Governance updates | docs/harness/PROJECT_BOARD.md, TASK_QUEUE.md, DECISION_RECORD.md, RISK_REGISTER.md, RUN_LOG.md, EVIDENCE_INDEX.md | P6-000 done. P6-M1 ready_with_approval. P6-M2 through P6-M11 blocked. P7-000 blocked. 8 decisions (P6-000-01 through P6-000-08). 8 risks (R-092 through R-099). |
| P6-CODE-COMPLETE | P6 runtime backend | apps/api/src/alters_lab/schemas/*, apps/api/src/alters_lab/services/*, apps/api/src/alters_lab/api/* | P6-M1 through P6-M11 backend schemas/services/routes implemented with P6 runtime helper and ignored product runtime areas. |
| P6-CODE-COMPLETE | P6 tests | apps/api/tests/test_obsidian_weekly_note.py, test_obsidian_weekly_note_api.py, test_p6_runtime_full.py, test_p6_runtime_api.py | 29 P6-focused tests added. Full backend suite: 833 tests passing. |
| P6-CODE-COMPLETE | P6 code-complete evidence | docs/harness/P6_CODE_COMPLETE_EVIDENCE.json | Sanitized evidence summary. Records code complete only; does not claim P6 behavior validation or closeout. |
| P6-CODE-COMPLETE-R1 | Behavior validation blocker repair | apps/api/src/alters_lab/services/behavior_validation.py, apps/api/src/alters_lab/services/phase6_closeout.py, apps/api/tests/test_p6_runtime_full.py, apps/api/tests/test_p6_runtime_api.py | Fixes fake-ID validation loophole. Requires persisted evidence and 4-week window. Adds tests for fake IDs, missing weekly/calibration/pattern records, short window, real 4-week validation, and manual fake closeout block. 840 backend tests passing. |
| P6-ENDGAME | Real-use validation runbook | docs/harness/P6_ENDGAME_REAL_USE_VALIDATION_RUNBOOK.md | Operator process for Week 1-4 real-use validation, pattern review, behavior validation, closeout, and failure branches. Does not claim validation. |
| P6-ENDGAME | Weekly review template | docs/harness/P6_WEEKLY_REVIEW_TEMPLATE.md | Obsidian weekly note template for real weekly notes. Raw notes remain runtime/private unless explicitly sanitized. |
| P6-ENDGAME | Validation checklist | docs/harness/P6_VALIDATION_CHECKLIST.md | Checklist for required weekly reviews, calibration records, pattern review, 4-week window, usage integrity, validation result, and closeout report. |
| P7-000 | Local app distribution plan | docs/harness/P7_000_LOCAL_APP_DISTRIBUTION_PLAN.md | P7 current state, product goal, non-goals, runtime layout, provider/frontend/packaging policies, P6 interaction, and milestone map. |
| P7-000 | P7 taskbook | docs/harness/P7_TASKBOOK.md | One-page execution summary, milestone table, dependencies, and PASS/BLOCKED criteria. |
| P7-000 | Runtime layout | docs/harness/P7_RUNTIME_LAYOUT.md | Exact production paths, config schema draft, migration notes, and dev/prod detection strategy. |
| P7-000 | Packaging boundary | docs/harness/P7_PACKAGING_BOUNDARY.md | Debian package contents, installed/not-installed files, user data preservation, desktop integration, and smoke test checklist. |
| P7-M1 | Runtime layout service | apps/api/src/alters_lab/services/runtime_layout.py | Dev/packaged runtime resolver, config helpers, redacted config status, and chmod 0600 secrets fallback helper. |
| P7-M1 | P6 runtime integration | apps/api/src/alters_lab/services/p6_runtime.py | Runtime helper accepts layout/mode while preserving explicit repo_root behavior; packaged writes target user data product dirs. |
| P7-M1 | Runtime layout API | apps/api/src/alters_lab/api/runtime_layout.py, apps/api/src/alters_lab/schemas/runtime_layout.py | `/runtime-layout/health`, `/status`, and `/ensure-config`; status redacts secrets and ensure-config creates config only. |
| P7-M1 | Runtime layout tests | apps/api/tests/test_runtime_layout.py, apps/api/tests/test_runtime_layout_api.py | Tests dev/default paths, packaged paths, env mode, repo_root compatibility, packaged P6 writes, config creation, 0600 secrets fallback, API redaction, and safety flags. |
| P7-M2 | Local app service | apps/api/src/alters_lab/services/local_app.py | Resolves frontend dist, reports local app status, serves index/assets, blocks API-prefix SPA fallback, and keeps missing dist non-fatal. |
| P7-M2 | Local app API | apps/api/src/alters_lab/api/local_app.py, apps/api/src/alters_lab/schemas/local_app.py | `/local-app/health`, `/local-app/status`, and `/local-app/frontend-status` with redacted provider and P6 not validated/not sealed flags. |
| P7-M2 | Local app tests | apps/api/tests/test_local_app.py, apps/api/tests/test_local_app_api.py | Tests dist resolution, frontend availability, static root/assets, SPA fallback, API route preservation, path traversal rejection, and P6 safety flags. |
| P7-M2 | Frontend build lockfile | apps/web/package-lock.json | Reproducible npm dependency lock for frontend build used by local app serving and future packaging. |
| P7-M3 | Local launcher service | apps/api/src/alters_lab/services/local_launcher.py | PID/log path helpers, process detection, port checks, start/stop/status/open/doctor service behavior, and localhost default. |
| P7-M3 | CLI entrypoint | apps/api/src/alters_lab/cli/__main__.py, apps/api/src/alters_lab/cli/launcher.py, apps/api/src/alters_lab/cli/__init__.py, apps/api/pyproject.toml | `python -m alters_lab.cli` and package script `alters-lab` for start/stop/status/open/doctor commands. |
| P7-M3 | Local launcher tests | apps/api/tests/test_local_launcher.py, apps/api/tests/test_local_launcher_cli.py | Tests parser commands, dry-run start, status, doctor, stale PID cleanup, stop safety, open dry-run, dev/packaged PID/log paths, and P6 false flags. |
| P7-M4 | Provider config schemas | apps/api/src/alters_lab/schemas/provider_config.py | Pydantic contracts for provider modes, redacted status/config, secret mutations, and dry-run provider tests. |
| P7-M4 | Provider config service | apps/api/src/alters_lab/services/provider_config.py | Local config resolver/writer, optional keyring detection, chmod 0600 fallback secrets file, redacted status, and dry-run/no-network provider checks. |
| P7-M4 | Provider config API | apps/api/src/alters_lab/api/provider_config.py | `/provider-config/health`, `/status`, `/config`, `/secret`, and `/test`; config and status never return API keys. |
| P7-M4 | Provider Settings frontend | apps/web/src/pages/ProviderSettings.tsx, apps/web/src/App.tsx, apps/web/src/api.ts | UI for mode/base_url/model/timeout/secret storage/API key store-delete/dry-run test; stored key is never displayed or persisted in localStorage. |
| P7-M4 | Provider config tests | apps/api/tests/test_provider_config.py, apps/api/tests/test_provider_config_api.py | Tests default disabled, redaction, config-only writes, explicit real provider config, fallback chmod 0600, secret delete, dry-run provider tests, and P6 false flags. |
| P7-M5 | Debian package build script | tools/build_deb.py | Builds frontend, stages package filesystem, creates `/usr/bin/alters-lab`, builds package-local venv, excludes secrets/runtime/user data, and invokes `dpkg-deb`. |
| P7-M5 | Debian package metadata | packaging/deb/control.template, packaging/deb/postinst, packaging/deb/prerm, packaging/deb/postrm, packaging/deb/README.md | Package metadata and safe maintainer scripts that do not start services or delete user data. |
| P7-M5 | Debian package build docs | docs/harness/P7_DEBIAN_PACKAGE_BUILD.md | Package contents, launcher behavior, exclusions, data safety, and P6 boundary. |
| P7-M5 | Debian package tests | apps/api/tests/test_deb_package_build.py | Tests package paths, control metadata, launcher content, exclusions, maintainer script safety, gitignore outputs, and P6 unvalidated/unsealed docs. |
| P7-M6 | Desktop file | packaging/deb/alters-lab.desktop | Desktop entry that launches `alters-lab open`, with `Terminal=false`, Utility/Productivity categories, and no repo/user-home paths. |
| P7-M6 | Desktop icon | packaging/assets/alters-lab.svg | Small project-owned SVG icon staged as hicolor scalable app icon. |
| P7-M6 | Desktop integration docs | docs/harness/P7_DESKTOP_INTEGRATION.md | Desktop file path, icon path, package staging, and P6 boundary. |
| P7-M6 | Desktop package staging | tools/build_deb.py, apps/api/tests/test_deb_package_build.py | Build script stages desktop file/icon; tests cover source desktop file, unsafe token absence, icon staging, and P6 state docs. |
| P7-M7 | Data safety service | apps/api/src/alters_lab/services/data_safety.py | User data manifest, backup plan/archive creation, secret confirmation gate, package contents safety checks, and maintainer script checks. |
| P7-M7 | Backup CLI | apps/api/src/alters_lab/cli/launcher.py | `alters-lab backup` with dry-run/json/output/log/config/secret options and P6 false flags. |
| P7-M7 | Debian safety inspector | tools/inspect_deb_safety.py | Checks built package for required app/launcher/desktop/icon paths and forbidden user data/runtime/secret paths. |
| P7-M7 | Data safety tests | apps/api/tests/test_data_safety.py, apps/api/tests/test_local_launcher_cli.py, apps/api/tests/test_deb_package_build.py | Tests backup defaults, logs/secrets behavior, archive contents, CLI backup dry-run, package forbidden fragments, and maintainer scripts. |
| P7-M7 | Data safety docs | docs/harness/P7_DATA_SAFETY.md | Upgrade/remove/purge policy, backup policy, secret exclusion rationale, and P6 boundary. |
| P7-M8 | Local app smoke runner | tools/p7_local_app_smoke.py | Extracts built `.deb`, runs packaged CLI/server with isolated HOME, verifies frontend/provider/runtime-data/backup behavior, redacts temp paths, and keeps P6 flags false. |
| P7-M8 | Release candidate evidence | docs/harness/P7_M8_RELEASE_CANDIDATE_EVIDENCE.json | Sanitized package-context smoke evidence showing PASS, redacted provider status, isolated runtime record paths, backup dry-run, server cleanup, and P6 not validated/not sealed. |
| P7-M8 | Release candidate report | docs/harness/P7_LOCAL_APP_RELEASE_CANDIDATE.md | Human-readable P7-M8 method, checks, runtime layout observed, evidence artifacts, and boundary confirmations. |
| P7-M9 | P7 closeout report | docs/harness/P7_CLOSEOUT_REPORT.md | Final Phase 7 local app release candidate closeout report with capability summary, verification results, preserved boundaries, known limitations, and P6/P8 state. |
| P7-M9 | P7 closeout evidence | docs/harness/P7_CLOSEOUT_EVIDENCE.json | Structured P7 closeout evidence: milestone statuses, test/build/package/smoke results, boundary confirmations, artifacts, known limitations, P6 state, and P8 state. |
| P7-R1 | Frontend usability report | docs/harness/P7_FRONTEND_USABILITY_R1.md | Documents Weekly Review frontend flow, P6 progress panel, Status/Provider/Reality Score/History usability fixes, API calls wired, verification, and boundaries. |
| P7-R1 | Weekly Review UI | apps/web/src/pages/WeeklyReview.tsx, apps/web/src/pages/P6Progress.tsx | Primary P6 frontend entry point for weekly note ingest, review session completion, action alignment scoring, and progress tracking. |
| P6-ENDGAME | Closeout operator guide | docs/harness/P6_CLOSEOUT_OPERATOR_GUIDE.md | Guarded closeout instructions that keep P6 blocked unless behavior validation passes with verified persisted evidence. |
| P6-ENDGAME | Helper scripts | tools/p6_weekly_review_flow.py, tools/p6_validation_check.py, tools/p6_closeout_attempt.py | Local operator helpers. Weekly flow writes ignored runtime records only from supplied real notes; validation check is read-only; closeout attempt blocks without complete evidence. |
| P6-ENDGAME | Helper script tests | apps/api/tests/test_p6_endgame_tools.py | Tests empty evidence remains blocked, dry-run closeout remains blocked, and weekly flow writes records only under a supplied repo root. |
| DOCS-R1 | New session bootstrap | docs/harness/START_HERE_FOR_NEW_SESSION.md | First-read doc for new ChatGPT/Codex/Claude sessions. States current phase state, reading order, do-not-do list, and verification commands. |
| DOCS-R1 | Session context | docs/harness/CURRENT_SESSION_CONTEXT.md | Current session state: what was just completed, next decision, verification commands, and key boundaries. |
| P8-000 | P8 plan | docs/harness/P8_000_REAL_PROVIDER_AND_PRODUCT_READINESS_PLAN.md | Real provider and product readiness boundary plan: current state, milestone table, threat model, safety policy, E2E validation plan, required artifacts, hard boundaries, excluded scope. |
| P8-000 | P8 taskbook | docs/harness/P8_TASKBOOK.md | P8 milestone taskbook: P8-000 through P8-M7 with status, goals, dependencies, and notes. |
| P8-000 | Provider safety boundary | docs/harness/P8_PROVIDER_SAFETY_BOUNDARY.md | Provider safety rules: secret handling, provider output handling, network behavior, UI behavior, audit events. |
| P8-000 | E2E validation plan | docs/harness/P8_E2E_VALIDATION_PLAN.md | E2E validation plan: 5 test levels from mock-only to frontend flow smoke, pass criteria, excluded scope. |
| P8-M1 | Provider adapter schemas | apps/api/src/alters_lab/schemas/provider_adapter.py | ProviderAdapterRequest, ProviderAdapterResponse, ProviderAuditEvent, health/status responses. |
| P8-M1 | Provider adapter service | apps/api/src/alters_lab/services/provider_adapter.py | build_provider_adapter_health/status/audit_event, redact_provider_error, validate_provider_request, run_provider_adapter. |
| P8-M1 | Provider adapter API | apps/api/src/alters_lab/api/provider_adapter.py | Routes: /provider-adapter/health, /status, /preview. |
| P8-M1 | Provider adapter tests | apps/api/tests/test_provider_adapter.py, apps/api/tests/test_provider_adapter_api.py | 26 tests covering disabled/mock/openai modes, live_check blocked, persist_output blocked, no secrets, no YAML writes, no scores, safety flags. |
| P8-M1 | P8-M1 contract doc | docs/harness/P8_M1_PROVIDER_ADAPTER_CONTRACT.md | Provider adapter contract definition, architecture, safety guarantees, and test coverage. |
| P8-M2 | Provider connectivity schemas | apps/api/src/alters_lab/schemas/provider_connectivity.py | ProviderConnectivityRequest, Response, AuditEvent, health/status responses with Literal-locked safety fields. |
| P8-M2 | Provider connectivity service | apps/api/src/alters_lab/services/provider_connectivity.py | build_provider_connectivity_status/audit_event, run_provider_connectivity_check with http_client injection. |
| P8-M2 | Provider connectivity API | apps/api/src/alters_lab/api/provider_connectivity.py | Routes: /provider-connectivity/health, /status, /check. |
| P8-M2 | Provider connectivity tests | apps/api/tests/test_provider_connectivity.py, apps/api/tests/test_provider_connectivity_api.py | 30 tests covering disabled/mock/openai modes, live_check confirmation gating, fake http_client, 2xx/401/timeout, no secrets, safety flags, contract hardening. |
| P8-M2 | P8-M2 contract doc | docs/harness/P8_M2_PROVIDER_CONNECTIVITY.md | Provider connectivity check definition, architecture, safety guarantees, and test coverage. |
| P8-M3 | Provider dialogue preview schemas | apps/api/src/alters_lab/schemas/provider_dialogue_preview.py | ProviderDialoguePreviewRequest, Response, AuditEvent, health/status responses with Literal-locked safety fields. |
| P8-M3 | Provider dialogue preview service | apps/api/src/alters_lab/services/provider_dialogue_preview.py | run_provider_dialogue_preview with /chat/completions, injectable http_client, prompt/system_prompt capping, exact confirmation gating. |
| P8-M3 | Provider dialogue preview API | apps/api/src/alters_lab/api/provider_dialogue_preview.py | Routes: /provider-dialogue-preview/health, /status, /generate. |
| P8-M3 | Provider dialogue preview tests | apps/api/tests/test_provider_dialogue_preview.py, apps/api/tests/test_provider_dialogue_preview_api.py | 36 tests covering disabled/mock/openai modes, confirmation gating, fake http_client, 2xx/401/timeout/invalid_response, no secrets, no YAML writes, safety flags, contract hardening. |
| P8-M3 | P8-M3 contract doc | docs/harness/P8_M3_PROVIDER_DIALOGUE_PREVIEW.md | Provider dialogue preview definition, architecture, safety guarantees, and test coverage. |
| P8-M4 | Weekly review assistant schemas | apps/api/src/alters_lab/schemas/weekly_review_assistant.py | WeeklyReviewAssistantRequest, Response, AuditEvent, health/status responses with Literal-locked safety fields. |
| P8-M4 | Weekly review assistant service | apps/api/src/alters_lab/services/weekly_review_assistant.py | run_weekly_review_assistant reuses provider_dialogue_preview, advisory-only suggestions, prompt builder with requested_help types. |
| P8-M4 | Weekly review assistant API | apps/api/src/alters_lab/api/weekly_review_assistant.py | Routes: /weekly-review-assistant/health, /status, /suggest. |
| P8-M4 | Weekly review assistant tests | apps/api/tests/test_weekly_review_assistant.py, apps/api/tests/test_weekly_review_assistant_api.py | 33 tests covering health/status, disabled/mock/openai modes, confirmation gating, safety invariants, prompt builder, copy-only UI, no auto-completion, no scores. |
| P8-M4 | Weekly review assistant frontend | apps/web/src/pages/WeeklyReview.tsx | Added Assistant Suggestion section in Step 4 with requested_help select, dry-run/live buttons, suggestion display, copy-to-field buttons. |
| P8-M4 | P8-M4 contract doc | docs/harness/P8_M4_WEEKLY_REVIEW_ASSISTANT_MODE.md | Weekly review assistant definition, architecture, safety guarantees, and test coverage. |
| P8-M5 | P8 E2E product smoke script | tools/p8_e2e_product_smoke.py | Package-context isolated HOME smoke validating all P8 provider paths, weekly review flow, backup/data safety. |
| P8-M5 | P8 E2E smoke tests | apps/api/tests/test_p8_e2e_product_smoke.py | 15 tests covering safe defaults, report contract, redaction, provider safety flags, P6 false flags. |
| P8-M5 | P8 E2E validation evidence | docs/harness/P8_M5_E2E_PRODUCT_VALIDATION_EVIDENCE.json | Redacted JSON evidence from P8 smoke run. |
| P8-M5 | P8-M5 contract doc | docs/harness/P8_M5_E2E_PRODUCT_VALIDATION.md | P8 E2E validation definition, smoke script architecture, safety guarantees. |
| P8-M6 | Provider safety audit tool | tools/p8_provider_safety_audit.py | 7-section audit: grep scan, route audit, live constants, schema safety, evidence contract, secret policy, mutation boundary. |
| P8-M6 | Provider safety audit tests | apps/api/tests/test_p8_provider_safety_audit.py | 35 tests covering classification, scan logic, all 7 audit sections, evidence contract. |
| P8-M6 | Provider safety audit evidence | docs/harness/P8_M6_PROVIDER_SAFETY_AUDIT_EVIDENCE.json | Section-level PASS results, summary counts, no raw content. |
| P8-M6 | P8-M6 contract doc | docs/harness/P8_M6_PROVIDER_SAFETY_AUDIT.md | Audit definition, patterns, classification rules, safety guarantees. |
| P8-M7 | P8 closeout report | docs/harness/P8_CLOSEOUT_REPORT.md | Sealed as REAL_PROVIDER_READY_LOCAL_APP. All milestones done. Verification results. |
| P8-M7 | P8 closeout evidence | docs/harness/P8_CLOSEOUT_EVIDENCE.json | Verification results, milestone table, provider capabilities, safety summary, known limitations. |
| P8-M5-R1 | Redaction functions | tools/p8_e2e_product_smoke.py | _REDACT_FIELDS, _PROVIDER_OUTPUT_PATTERNS, _redact_sensitive_fields, _redact_string_value for evidence redaction. |
| P8-M5-R1 | Redaction tests | apps/api/tests/test_p8_e2e_product_smoke.py | 7 redaction tests + 1 committed evidence test. 22 total smoke tests. |
| P8-M6 | Safety audit tool | tools/p8_provider_safety_audit.py | 7-section audit: grep scan, route audit, live constants, schema safety, evidence contract, secret policy, mutation boundary. |
| P8-M6 | Safety audit tests | apps/api/tests/test_p8_provider_safety_audit.py | 35 tests covering all 7 audit sections. |
| P8-M6 | Safety audit evidence | docs/harness/P8_M6_PROVIDER_SAFETY_AUDIT_EVIDENCE.json | Section-level PASS results, summary counts, no raw content. |
| P8-M6 | provider_config Literal[False] fix | apps/api/src/alters_lab/schemas/provider_config.py | Changed safety fields from bool to Literal[False]. |
| P8-M6 | provider_gateway public API fix | apps/api/src/alters_lab/services/provider_gateway.py | Changed _resolve_secret to use public get_secret. |
| P8-M7 | P8 closeout report | docs/harness/P8_CLOSEOUT_REPORT.md | Full verification table, 12 checks all PASS. |
| P8-M7 | P8 closeout evidence | docs/harness/P8_CLOSEOUT_EVIDENCE.json | Structured evidence with all verification results. |
| P9-000 | P9 plan | docs/harness/P9_000_RELEASE_HYGIENE_AND_INSTALL_READINESS_PLAN.md | Release hygiene boundary plan with milestone table, threat model, success standard, hard boundaries. |
| P9-000 | P9 taskbook | docs/harness/P9_TASKBOOK.md | P9 milestone taskbook: P9-000 through P9-M7. |
| P9-000 | Release readiness boundary | docs/harness/P9_RELEASE_READINESS_BOUNDARY.md | Hard boundaries, success standard, threat model. |
| P9-000 | User-facing docs plan | docs/harness/P9_USER_FACING_DOCS_PLAN.md | 5 docs to create, 3 docs to update, review process. |
| P9-M1 | Install guide | docs/user/INSTALL.md | System requirements, install from .deb, build from source, installed paths, data paths, verification. |
| P9-M1 | First run guide | docs/user/FIRST_RUN.md | Launch, what is Alters Lab, provider mode, smoke test, P6/P7/P8 explanation, weekly review, stopping. |
| P9-M1 | Uninstall guide | docs/user/UNINSTALL.md | Stop, remove, what's removed/preserved, full cleanup, reinstall, upgrade. |
| P9-M1 | Data and backup guide | docs/user/DATA_AND_BACKUP.md | Data paths, backup command, options, restore, data safety, P6 runtime records. |
| P9-M2 | Lifecycle smoke script | tools/p9_package_lifecycle_smoke.py | Disposable dpkg lifecycle smoke: install/upgrade/remove in fakeroot. Evidence redaction, safety flags. |
| P9-M2 | Lifecycle smoke tests | apps/api/tests/test_p9_package_lifecycle_smoke.py | 25 tests: arg parsing, redaction, report contract, safety flags. |
| P9-M2 | Verification doc | docs/harness/P9_M2_DISPOSABLE_INSTALL_VERIFICATION.md | Method, what it verifies, evidence redaction, hard boundaries, test coverage, usage. |
| P9-M3 | First-run checklist | docs/user/FIRST_RUN_CHECKLIST.md | 13-item user-facing checklist: install verification, open app, doctor, provider disabled default, mock mode, weekly note import, weekly review, backup, P6 boundary, provider advisory, project phases, next steps. |
| P9-M3 | Getting Started page | apps/web/src/pages/GettingStarted.tsx | Frontend onboarding page with 4 sections: provider disabled, weekly review, doctor, backup + boundary copy. Static checklist with nav buttons. |
| P9-M3 | App.tsx update | apps/web/src/App.tsx | Added 'getting-started' page type and Getting Started nav button. |
| P9-M3 | FIRST_RUN.md update | docs/user/FIRST_RUN.md | Added link to FIRST_RUN_CHECKLIST.md. |
| P9-M3 | INSTALL.md update | docs/user/INSTALL.md | Added Next Steps section linking to FIRST_RUN_CHECKLIST.md. |
| P9-M3 | README.md update | README.md | Added First-Run Checklist link to Documentation section. |
| P9-M4 | Provider setup guide | docs/user/PROVIDER_SETUP.md | Provider modes (disabled/mock/openai-compatible-http), required fields, dry-run test, confirmation gating, P8 meaning, no real API key examples. |
| P9-M4 | Provider safety guide | docs/user/PROVIDER_SAFETY.md | Secret storage, API key handling, backup behavior, output safety boundaries, confirmation gating table, network behavior, P6 boundary. |
| P9-M4 | ProviderSettings.tsx update | apps/web/src/pages/ProviderSettings.tsx | Added safety notes panel: disabled default, mock no-network, live confirmation-gated, output advisory, key never displayed, links to docs. |
| P9-M4 | FIRST_RUN.md update | docs/user/FIRST_RUN.md | Replaced inline provider setup with links to PROVIDER_SETUP.md and PROVIDER_SAFETY.md. |
| P9-M4 | README.md update | README.md | Added Provider Setup and Provider Safety links to Documentation section. |
| P9-M4-R1 | PROVIDER_SETUP.md fix | docs/user/PROVIDER_SETUP.md | Corrected dry-run wording: verifies local config only, no network. Added live connectivity check section. |
| P9-M4-R1 | PROVIDER_SAFETY.md fix | docs/user/PROVIDER_SAFETY.md | Updated confirmation table with Network Call column distinguishing dry-run (no network) from live connectivity (may call /models). |
| P9-M5 | Enhanced doctor report | apps/api/src/alters_lab/services/local_launcher.py | New checks: app_root_exists, config_exists, product_data_dir_writable, state_dir_writable, provider_configured, secrets_file (0600 permissions), actionable WARN/BLOCKED messages. |
| P9-M5 | Troubleshooting guide | docs/user/TROUBLESHOOTING.md | 12 scenarios: app won't start, browser, port conflict, command missing, frontend 503, provider issues (disabled/mock/live), keyring, secrets perms, backup, uninstall data, P6, logs. |
| P9-M5 | Doctor tests | apps/api/tests/test_local_launcher.py, apps/api/tests/test_local_launcher_cli.py | 10 new tests: checks list, API key absence, provider mode, P6 flags, data dirs, safety flags, actionable messages, text output. |
| P9-M5 | Doc updates | docs/user/INSTALL.md, FIRST_RUN.md, DATA_AND_BACKUP.md, UNINSTALL.md, README.md | Added TROUBLESHOOTING.md links. |
| P9-M6 | Release checklist | docs/harness/P9_RELEASE_CHECKLIST.md | Pre-release checks (backend tests, frontend build, package build, package safety, lifecycle smoke, forbidden claims, secret check, doctor output), doc checks, governance checks, post-release. |
| P9-M6 | Version bump policy | docs/harness/P9_VERSION_BUMP_POLICY.md | SemVer rules (PATCH/MINOR/MAJOR), current history 0.1.0, where version lives, phase completion relationship. |
| P9-M7 | P9 closeout report | docs/harness/P9_CLOSEOUT_REPORT.md | Final P9 closeout: milestone table, success standard verification, verification results, user docs list, governance artifacts, doctor improvements, preserved boundaries, known limitations. |
| P10-000 | P10_000_PERSONAL_PILOT_AND_REAL_USE_CUTOVER_PLAN.md | docs/harness/ | P10 boundary plan: scope, milestones, excluded scope, hard boundaries |
| P10-000 | P10_TASKBOOK.md | docs/harness/ | P10 milestone tracking |
| P10-000 | P10_REAL_USE_BOUNDARY.md | docs/harness/ | What counts as real use vs synthetic |
| P10-000 | P10_P6_VALIDATION_BRIDGE.md | docs/harness/ | P6 validation start conditions |
| P10-000 | P10_PILOT_EVIDENCE_REQUIREMENTS.md | docs/harness/ | Evidence collection and commit policy |
| P10-M1 | P10_M1_LOCAL_INSTALLATION_CUTOVER_CHECKLIST.md | docs/harness/ | 9-section operator checklist for packaged app cutover |
| P10-M1 | P10_M1_CUTOVER_EVIDENCE_TEMPLATE.md | docs/harness/ | Fillable redacted YAML evidence template |
| P10-M2 | P10_M2_FIRST_REAL_WEEKLY_NOTE_INGEST.md | docs/harness/ | Operator instructions for first real weekly note ingest |
| P10-M2 | P10_M2_REAL_WEEKLY_NOTE_EVIDENCE_TEMPLATE.md | docs/harness/ | Fillable redacted YAML evidence template |
| P10-M2 | P10_M2_REAL_WEEKLY_NOTE_INGEST_EVIDENCE.md | docs/harness/ | Real-use evidence: first weekly note ingested via packaged app |
| P10-M3 | P10_M3_FIRST_REAL_WEEKLY_REVIEW_SESSION.md | docs/harness/ | Operator instructions for first real weekly review session |
| P10-M3 | P10_M3_REAL_WEEKLY_REVIEW_EVIDENCE_TEMPLATE.md | docs/harness/ | Fillable redacted YAML evidence template for weekly review |
| P10-M3 | P10_M3_REAL_WEEKLY_REVIEW_EVIDENCE.md | docs/harness/ | Real-use evidence: first weekly review session completed via packaged app |
| P10-M4 | P10_M4_REAL_USE_FRICTION_LOG.md | docs/harness/ | Structured friction log from P10-M2/P10-M3 real use: 3 low-severity items, 0 blocker |
| P10-M4 | P10_M4_FIX_TRIAGE.md | docs/harness/ | Fix triage classification: 0 must-fix, 0 should-fix, 0 defer, 3 no-fix-needed |
| P10-M5 | P10_M5_P6_VALIDATION_START_DECISION.md | docs/harness/ | Decision gate: 3 options, GPT recommends START, awaiting Charlie's explicit decision |
| P10-M5 | P10_M5_P6_VALIDATION_START_EVIDENCE_TEMPLATE.md | docs/harness/ | Fillable evidence template for P6 validation start decision |
| P10-M5 | P10_M5_P6_VALIDATION_START_EVIDENCE.md | docs/harness/ | Decision evidence: BLOCKED_BY_NEW_FRICTION, product incompleteness |
| P11-000 | P11_000_PRODUCT_COMPLETENESS_BEFORE_VALIDATION_PLAN.md | docs/harness/ | P11 planning stub: audit and complete app before P6 validation |
| P11-M1 | P11_M1_APP_CAPABILITY_INVENTORY.md | docs/harness/ | Full app inventory: 9 pages, 124 routes, 6 CLI commands, 11 workflows (R1 updated) |
| P11-M1-R1 | P11_M1_DATA_RECORD_INVENTORY.md | docs/harness/ | Data record / local storage inventory: 20 record types, 12 P6 runtime areas, storage layout |
| P11-M1-R1 | P11_M1_ROUTE_AND_PAGE_INVENTORY.md | docs/harness/ | Per-route inventory: method, path, R/W, provider risk, frontend-used, status for 124 routes |
| P11-M1-R1 | P11_M1_USER_WORKFLOW_INVENTORY.md | docs/harness/ | User workflow inventory: 16 workflows with frontend path, APIs, records, gaps, P6 blocker status |
| P11-M2 | P11_M2_MISSING_CORE_WORKFLOW_MAP.md | docs/harness/ | Workflow tier classification: 23 workflows, 4 tiers, core missing workflows identified |
| P11-M2 | P11_M2_PRODUCT_COMPLETENESS_GAP_MATRIX.md | docs/harness/ | Gap matrix: 20 gaps with gap_id, tier, type, severity, blockers, recommended phase |
| P11-M2 | P11_M2_WORKFLOW_PRIORITY_DECISION.md | docs/harness/ | Priority decision: calibration/history visibility (M3), validation readiness (M4), defer Phase 3-6 frontends |
| P11-M3 | P11_M3_UX_GAPS_AND_NORMAL_USE_BLOCKERS.md | docs/harness/ | Normal-use journey audit (12 steps), page-level UX audit (10 pages), calibration/history UX findings, 12 UX gaps |
| P11-M3 | P11_M3_CALIBRATION_HISTORY_UX_ANALYSIS.md | docs/harness/ | CalibrationHistory UX analysis: current state, must-have/should-have/nice-to-have requirements, key insight |
| P11-M3 | P11_M3_NORMAL_USE_BLOCKER_DECISION.md | docs/harness/ | Blocker decision: 0 blockers, 0 high, 3 medium, 9 low. Normal weekly use works. P11-M4 can proceed. |
| P11-M4 | P11_M4_GAP_CLOSURE_PLAN.md | docs/harness/ | Gap closure plan: all M5/M6 features frontend-only, existing APIs sufficient, no backend changes |
| P11-M4 | P11_M4_IMPLEMENTATION_BATCH_PLAN.md | docs/harness/ | M5 batch: 5 items (CalibrationHistory, RealityScore, P6Progress, Step 5, Step 3). M6 batch: 3 items (PatternReview, BehaviorValidation, DataManagement) |
| P11-M4 | P11_M4_ACCEPTANCE_CRITERIA.md | docs/harness/ | Concrete acceptance criteria for M5 and M6 with build/test/feature/boundary checkboxes |
| P11-M4 | P11_M4_RISK_AND_BOUNDARY_REVIEW.md | docs/harness/ | Risk assessment, hard boundaries, no-go conditions, boundary confirmation checklist |
| P11-M5 | CalibrationHistory.tsx | apps/web/src/pages/ | Detail drill-down, trend indicator, score explanation, date sorting |
| P11-M5 | RealityScore.tsx | apps/web/src/pages/ | Recent scores section, CalibrationHistory link |
| P11-M5 | P6Progress.tsx | apps/web/src/pages/ | User-facing labels, validation status, next-step guidance |
| P11-M5 | WeeklyReview.tsx | apps/web/src/pages/ | Step 5 verdict descriptions, Step 3 dynamic alter loading |
| P11-M5-R1 | RealityScore.tsx | apps/web/src/pages/ | Fix navigation to use typed page callback |
| P11-M5-R1 | P6Progress.tsx | apps/web/src/pages/ | Fix validation wording to mention product completeness blocker |
| P11-M5-R1 | App.tsx | apps/web/src/ | Pass typed navigation callback to RealityScore |
| P11-M6 | PatternReview.tsx | apps/web/src/pages/ | Pattern review list/detail/build with P6 boundary copy |
| P11-M6 | BehaviorValidation.tsx | apps/web/src/pages/ | Validation report/evaluate with P6 not-started banner |
| P11-M6 | DataManagement.tsx | apps/web/src/pages/ | Record counts, export, manual delete, archive disabled notice |
| P11-M6 | App.tsx | apps/web/src/ | Wire Patterns/Validation/Data nav and router |
| P11-M6-R1 | DataManagement.tsx | apps/web/src/pages/ | Remove fabricated delete IDs, add manual record ID panel, archive disabled |
| P11-M6-R1 | PatternReview.tsx | apps/web/src/pages/ | Add P6/provider evidence boundary copy |
| P11-M7 | P11_M7_PRODUCT_COMPLETENESS_SMOKE_EVIDENCE.json | docs/harness/ | Smoke evidence: all builds pass, boundary checks pass, frontend content verified |
| P11-M7 | P11_CLOSEOUT_REPORT.md | docs/harness/ | P11 closeout: product completeness established, P6 remains NOT_VALIDATED |
| P11-M7 | P11_CLOSEOUT_EVIDENCE.json | docs/harness/ | Closeout evidence: all milestones PASS, P11 sealed |
| P11-PILOT-1 | P11-PILOT-1-real-use-product-pilot.md | docs/runs/ | Real-use product pilot: 10 workflows exercised, friction=none, boundary checks pass, GPT verdict PASS |
| P10-M5-R2 | P10_M5_R2_P6_VALIDATION_REENTRY_DECISION.md | docs/harness/ | Reopened P6 validation start gate using P11 closeout + P11-PILOT-1 evidence |
| P10-M5-R2 | P10_M5_R2_P6_VALIDATION_REENTRY_EVIDENCE_TEMPLATE.md | docs/harness/ | Fillable evidence template for P6 validation reentry decision |
| P10-M5-R2-E1 | P10_M5_R2_P6_VALIDATION_START_EVIDENCE.md | docs/harness/ | Charlie's START_P6_VALIDATION_NOW decision recorded, P6 state VALIDATION_IN_PROGRESS |
| P10-M6 | P10_M6_WEEK1_VALIDATION_PACKAGE.md | docs/harness/ | Week 1 validation package: what Charlie must do, countable records, non-countable evidence |
| P10-M6 | P10_M6_WEEK1_VALIDATION_EVIDENCE.md | docs/harness/ | Week 1 validation evidence (commit 14ee9d5): 1 review, 1 action alignment, 0 pattern reviews |
| P10-M6 | P10_M6_WEEK1_VALIDATION_EVIDENCE_TEMPLATE.md | docs/harness/ | Reusable evidence template for future validation weeks |
| P10-M6 | P10_M6_VALIDATION_COUNTERS.md | docs/harness/ | Validation counters: 1 review, 1 calibration record, 0 pattern reviews, 0 days elapsed |
| P10-M6-R1 | P10_M6_WEEK1_VALIDATION_EVIDENCE.md, P10_M6_WEEK1_VALIDATION_EVIDENCE_TEMPLATE.md, 6 governance docs | docs/harness/ | Finalize Week 1 validation evidence governance |
| P10-M6-CC1 | P10_M6_VALIDATION_WINDOW_CHANGE_CONTROL.md | docs/harness/ | Validation-window change control: allowed/disallowed changes during P6 validation |
| P10-M6-PREP1 | P10_M6_VALIDATION_RUNBOOK.md, P10_M6_WEEK2_VALIDATION_EVIDENCE_TEMPLATE.md, P10_M6_WEEK3_VALIDATION_EVIDENCE_TEMPLATE.md, P10_M6_WEEK4_VALIDATION_EVIDENCE_TEMPLATE.md | docs/harness/ | Validation runbook and future week evidence templates |
| P10-M6-UXT1 | P10_M6_UXT1_USABILITY_TRIAGE.md | docs/harness/ | Usability triage: 0 blocker, 0 high, 1 medium, 4 low. Week 2 can proceed. |
| DOC-HANDOFF-001 | AGENTS.md | ./ | Cross-agent bootstrap, hard boundaries, verification commands, and documentation maintenance rule |
| DOC-HANDOFF-001 | README.md, CLAUDE.md, START_HERE_FOR_NEW_SESSION.md, CURRENT_SESSION_CONTEXT.md | ./, docs/harness/ | Handoff surface updated so new sessions see P11/Pilot state and commit-time doc maintenance expectations |
| P12-000 | P12_000_UI_OVERRIDE_PLAN.md | docs/harness/ | Owner override plan: P6 validation paused for product change, P12 UI improvement milestones defined |
| P12-M1 | Tailwind CSS conversion (20 files) | apps/web/ | Tailwind v4 installed, all 13 pages converted from inline styles, dark theme applied, build passes |
| P12-M2 | LoadingSpinner component | apps/web/src/components/LoadingSpinner.tsx | Shared CSS-animated SVG spinner with optional label |
| P12-M2 | ErrorDisplay component | apps/web/src/components/ErrorDisplay.tsx | Shared error display with optional retry button |
| P12-M2 | Loading states (8 pages) | apps/web/src/pages/ | DataManagement, RealityScore, PatternReview, ProviderSettings, BehaviorValidation, SystemStatus, CalibrationHistory, P6Progress all updated with loading/error states |
| P12-M3 | i18n config | apps/web/src/i18n.ts | react-i18next setup with zh/en namespaces and manual localStorage persistence (default English) |
| P12-M3 | English locale | apps/web/src/locales/en.json | Full English translations for all UI strings across 15 pages/components |
| P12-M3 | Chinese locale | apps/web/src/locales/zh.json | Full Chinese translations for all UI strings across 15 pages/components |
| P12-M3 | Language toggle | apps/web/src/App.tsx | EN/ZH toggle button in header, nav bar labels translated |
| P12-M3 | Page i18n updates | apps/web/src/pages/ | All 15 pages/components updated with useTranslation() hook and t() calls |
| P12-M3-R1 | localStorage persistence | apps/web/src/i18n.ts, apps/web/src/App.tsx | Read/write localStorage "alters_lab_language" for language persistence, default English |
| P12-M4 | Guided onboarding wizard | apps/web/src/pages/GettingStarted.tsx | Step-by-step wizard with progress bar, expandable steps, localStorage-persisted completion |
| P12-M4 | Guided path translations | apps/web/src/locales/en.json, apps/web/src/locales/zh.json | Updated gettingStarted section with guided path step titles, descriptions, actions |
| P12-M5 | GSAP animations | apps/web/src/animations.ts | fadeIn, expandIn, collapseOut, pulseSuccess, shakeError utilities |
| P12-M5 | Page entry animation | apps/web/src/App.tsx | Fade-in animation on page transitions |
| P12-M5 | Error animation | apps/web/src/components/ErrorDisplay.tsx | Fade-in and shake animation on error display |
