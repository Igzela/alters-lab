# Quality Gates

## Non-Negotiable Gates

### Branch Structural Incompatibility

Branches must be structurally and mutually incompatible. They differ in kind, not degree. A branch that is "the same thing but more/less" is not a valid branch — it is a gradation. Quality gate: each branch must have a clear structural_difference that makes it incompatible with all other branches in the set.

### Alter Branch Reference

Every Alter must reference a valid branch_ref. An Alter without a branch is invalid. Quality gate: alter.yaml must contain a branch_ref field pointing to an existing branch ID.

### Time Horizon Fixed

Branch time horizon is fixed at 1.5-2 years. Branches that project beyond or fall short of this window are invalid. Quality gate: all branches must have a consistent time horizon within the 1.5-2 year range.

### Dialogue Full Inject

Dialogue sessions must inject the full alter.yaml content. Summarised or truncated alter content invalidates the dialogue. Quality gate: dialogue input must contain complete alter data.

### Rubric Cannot Auto-Modify

The rubric cannot modify itself. All rubric changes require explicit human review and approval. Quality gate: auto_modify field on rubric is always false; any rubric version bump requires documented human decision.

### Unknown Error Requires Human Review

Any unknown_error during system operation requires human review. Automated retry or silent failure is not permitted. Quality gate: unknown_error events are logged and escalated to human.

### Snapshot Intake

The snapshot must use canonical Phase 0 structure with all required fields present. Quality gate:
- **Pass**: snapshot.yaml has canonical structure, all three anchors exist (heaviest_constraint, most_unclear, unwilling_to_give_up), intake_status exists, empty fields are empty strings/lists (not invented content).
- **Fail**: multiple questions asked at once, branches generated before snapshot confirmation, alters generated during intake, snapshot contains invented placeholder data.

### Branch Discovery

Branch Discovery must produce 3-4 structural, mutually incompatible branches from confirmed snapshot anchors. Quality gate:
- **Pass**: branch_discovery.status is "completed", branches list has 3-4 entries, each branch has id, core_choice, structural_commitment, key_tension_resolved, incompatible_with (non-empty), preserves, sacrifices, validation_signal_30d, invalid_if; every branch in incompatible_with exists in branches list; no branch differs only in result or parameter from another.
- **Fail**: fewer than 3 branches, more than 4 branches, any branch with empty incompatible_with, any branch pair that is compatible (not structurally conflicting), branches generated from unconfirmed snapshot, branches contain invented data not traced to snapshot anchors.

### Alter Generation

Alter Generation produces one Alter per confirmed branch with coherent voice, tradeoffs, and personality drift. Quality gate:
- **Pass**: alter_*.yaml files exist only for human-confirmed branches; each alter has branch_ref pointing to existing branch, snapshot_ref pointing to current snapshot, time_horizon of "1.5-2年后", non-empty voice with core_stance (not neutral), concrete tradeoffs (gained and lost non-empty), personality_drift with direction and reason for each dimension, no probability predictions, no neutral advice-bot voice.
- **Fail**: alter generated from unconfirmed/empty branch, missing branch_ref, voice is neutral/generic, contains probability prediction, empty tradeoffs, personality drift has no reason, generated without human confirmation.

### Dialogue Engine

Dialogue Engine facilitates exploration between user and confirmed Alter. Quality gate:
- **Pass**: dialogue session references existing alter_*.yaml with full injection (not summary), alter speaks from future-self perspective with branch-specific grounding, grounding metadata present on every response (alter_sections_used, branch_fields_used, snapshot_fields_used), no probability claims, no generic advice-bot voice, no governance authority claims, no rubric modifications, no invented content, session created only after human confirmation, no active sessions from empty alters.
- **Fail**: summary-only alter injection, alter drifts into neutral voice, probability claims present, session created without confirmed alter, grounding metadata missing, dialogue content invented for nonexistent Alters, no human confirmation before session start.

### Value Alignment Evaluator

Value Alignment Evaluator compares Alters against user-confirmed values. Quality gate:
- **Pass**: snapshot completed (intake_status.phase: "completed"), branches confirmed (3-4 with non-empty incompatible_with), active alters exist (alter_*.yaml with branch_ref), value profile is user-confirmed only (no invented values), all five alignment dimensions assessed (autonomy, stability, exploration, engineering_output, relationship_life), comparison matrix produced (strongest, weakest, unresolved tradeoffs), requires_human_review is true, no active alignment_*.yaml files exist, no auto-choice, no rubric modification, no calibration update.
- **Fail**: evaluator proceeds without confirmed snapshot/branches/alters, value profile contains invented data, any dimension skipped, auto-choice made without human review, alignment_*.yaml files created, rubric modified, calibration updated, incomplete comparison matrix.

### Calibration + Rubric

Calibration scores branches against reality using a fixed rubric with four dimensions. Quality gate:
- **Pass**: rubric.yaml has canonical structure (version, mode, status, dimensions, drift_formula, evolution_policy with auto_modify: false), state.json has cold_start state, scores/_template.yaml exists and is marked inactive_template_only, no active score_*.yaml files exist, no drift computed, no rubric evolution, calibration-system-workflow.md documents all sections (purpose, inputs, two-speed model, dimensions, cold-start policy, evolution policy, valid/invalid, hard prohibitions).
- **Fail**: rubric auto_modify is true, active score files created without confirmed inputs, drift computed without both predicted and actual values, rubric modified without human confirmation, invented values used for scoring, Brier scoring used, cold-start scoring attempted before baseline established.

### Archive System

Archive System preserves historical system states at meaningful checkpoints. Quality gate:
- **Pass**: archive/_template/ folder exists with all 7 template files (snapshot.yaml, branches.yaml, reality_trace.yaml, reality_score.yaml, resolution.yaml, rubric_delta.yaml, alters/.gitkeep); all templates marked inactive_template_only and status: inactive_template_only; archive-system-workflow.md exists with all 9 sections (purpose, input requirements, folder naming, archive contents, triggers, process, valid/invalid, rubric delta policy, hard prohibitions); no real dated archive folders created; no active current files mutated; no rubric delta applied; reject_auto_apply is true on rubric_delta template.
- **Fail**: any archive template missing, any template not marked inactive_template_only, real dated archive folder created, active current files modified, rubric delta applied without human confirmation, reject_auto_apply is not true, archive created without snapshot or branches, archive created during active operations.

## Quality Checklist

- [ ] All branches are structurally and mutually incompatible
- [ ] All Alters reference a valid branch_ref
- [ ] All branches have 1.5-2 year time horizon
- [ ] Dialogue injects full alter.yaml
- [ ] Rubric auto_modify is false
- [ ] Unknown errors escalate to human review
- [ ] Snapshot uses canonical Phase 0 structure
- [ ] All three anchors present in snapshot
- [ ] No branches or alters before snapshot confirmation
- [ ] Branch Discovery produces 3-4 branches from confirmed snapshot
- [ ] Every branch has non-empty incompatible_with
- [ ] No result-only or parameter-only branch differences
- [ ] Alter Generation produces valid alters only from confirmed branches
- [ ] Each alter has branch_ref, voice with stance, concrete tradeoffs
- [ ] No probability predictions or neutral advice-bot voice in alters
- [ ] No active alter_*.yaml without human confirmation
- [ ] Dialogue injects full alter.yaml (not summary)
- [ ] Alter speaks from future-self with branch-specific grounding
- [ ] Grounding metadata present on every Alter response
- [ ] No probability claims or generic advice-bot voice in dialogue
- [ ] No active dialogue sessions from empty alters
- [ ] No invented content in dialogue
- [ ] Value Alignment proceeds only with confirmed snapshot, branches, and alters
- [ ] Value profile is user-confirmed only, no invented values
- [ ] All five alignment dimensions assessed per Alter
- [ ] Comparison matrix produced with strongest, weakest, unresolved
- [ ] requires_human_review is true on all alignment reports
- [ ] No active alignment_*.yaml files created
- [ ] No auto-choice, no rubric modification, no calibration update
- [ ] Rubric auto_modify is false, mode is cold_start
- [ ] No active score_*.yaml files in Phase 0
- [ ] No drift computed without both predicted and actual values
- [ ] No rubric evolution without human confirmation
- [ ] No Brier scoring used
- [ ] Cold-start policy documented and followed
- [ ] Archive _template folder has all 7 files
- [ ] All archive templates marked inactive_template_only
- [ ] No real dated archive folders created
- [ ] No active current files mutated during archive
- [ ] No rubric delta applied without human confirmation
- [ ] reject_auto_apply is true on rubric_delta template
- [ ] Archive process requires snapshot and branches to exist
