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
