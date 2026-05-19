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
