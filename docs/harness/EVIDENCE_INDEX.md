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
