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
