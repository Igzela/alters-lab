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
