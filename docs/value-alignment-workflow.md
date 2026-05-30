> **Note**: This is a historical design document. Phase references (Phase 0, P4) reflect the system's state at time of writing. For current status, see CLAUDE.md.

# Value Alignment Evaluator Workflow

## A. Purpose

The Value Alignment Evaluator compares confirmed Alters against user-confirmed values. It does not choose a branch. It does not score alignment automatically. It produces a structured comparison that requires human review before any decision is made.

The evaluator answers: "Which Alter best fits what the user actually values, and what must be sacrificed in each path?" It does not answer: "Which path is best?"

## B. Input Requirements

The evaluator requires three conditions before it can proceed:

1. **Snapshot completed** — `alters/current/snapshot.yaml` has `intake_status.phase: "completed"` and all three anchors are filled.
2. **Branches confirmed** — `alters/current/branches.yaml` has 3-4 confirmed branches with non-empty `incompatible_with`.
3. **Active alters exist** — `alters/current/alters/alter_*.yaml` files exist with `template_status: "active"`, each referencing a valid `branch_ref`.

If any of these conditions are not met, the evaluator is **blocked** and must not proceed.

## C. Value Extraction from User-Confirmed Data Only

Values are extracted exclusively from user-confirmed data. The evaluator must not invent, infer, or assume user values.

Sources of value data:
- **Snapshot anchors**: `heaviest_constraint`, `most_unclear`, `unwilling_to_give_up` — these reveal non-negotiables.
- **Branch tradeoffs**: `preserves` and `sacrifices` on each branch — these reveal value priorities.
- **Dialogue sessions** (if any exist): user responses during dialogue reveal preferences and tradeoff tolerances.

Forbidden sources:
- Any invented value profile.
- Any inference from branch content alone (e.g., "this branch values stability" is an inference, not a user confirmation).
- Any external data or LLM-generated assumptions about user values.

The `value_profile` in `_template.yaml` remains `status: "not_started"` until the user explicitly confirms their values through the intake process.

## D. Alignment Dimensions

The evaluator compares Alters along five fixed alignment dimensions:

| Dimension | What It Measures |
|-----------|-----------------|
| **autonomy** | Degree of self-direction and independence in the chosen path |
| **stability** | Predictability, safety, and reduced uncertainty |
| **exploration** | Novelty, learning, and exposure to unknown outcomes |
| **engineering_output** | Tangible creation, building, and technical contribution |
| **relationship_life** | Impact on relationships, social connections, and interpersonal bonds |

These dimensions are fixed for Phase 0. They cannot be modified, extended, or weighted automatically. Any changes require explicit human review and a documented decision record.

## E. Evaluation Pipeline

The evaluation follows a four-step pipeline:

### Step 1: Value Profile Construction

Extract and confirm the user's value profile from snapshot anchors and dialogue data. This step is **manual** — the user must confirm each value.

Output: `value_profile` with confirmed `primary_non_negotiable`, `secondary_non_negotiables`, `willing_to_sacrifice`, and `weak_fit_paths`.

### Step 2: Per-Alter Alignment Mapping

For each active Alter, map its tradeoffs (`gained` and `lost`) against the five alignment dimensions. This step identifies which dimensions each Alter strengthens and which it weakens.

Output: Per-alter alignment notes on each dimension.

### Step 3: Comparison Matrix

Compare all Alters side-by-side across the five dimensions. Identify:
- **Strongest alignment**: Which Alter best fits the confirmed value profile.
- **Weakest alignment**: Which Alter most conflicts with confirmed values.
- **Unresolved tradeoffs**: Where two Alters trade off equally on different dimensions.

Output: `comparison` block with strongest, weakest, and unresolved entries.

### Step 4: Human Review Gate

The evaluator produces a report but **cannot finalize it**. All alignment reports require human review. The human must:
- Confirm or override the strongest/weakest assessment.
- Resolve unresolved tradeoffs.
- Decide whether to proceed with any branch or re-run intake.

Output: `alignment_report` with `status: "pending_human_review"`.

## F. Valid/Invalid Alignment Patterns

### Valid Patterns

- All five dimensions are assessed for each Alter.
- Strongest and weakest alignment are identified with supporting evidence.
- Unresolved tradeoffs are listed explicitly.
- `requires_human_review` is true.
- `status` is `"pending_human_review"` or `"not_started"`.

### Invalid Patterns

- Auto-choice: evaluator selects a branch without human review.
- Incomplete dimensions: any dimension is skipped or marked "not applicable".
- No comparison: only one Alter is evaluated when multiple exist.
- Invented values: value profile contains data not confirmed by the user.
- Completed status without human review: `status` is `"completed"` without documented human decision.

## G. Human Confirmation Required

The Value Alignment Evaluator is a **decision-support tool**, not a decision-making tool.

Every alignment report requires human confirmation before it is considered valid. The human must:

1. **Review the comparison matrix** — read each Alter's alignment against the five dimensions.
2. **Confirm or override assessments** — agree with the evaluator's mapping or correct it.
3. **Resolve tradeoffs** — where two Alters trade off equally, the human must decide which dimension matters more.
4. **Document the decision** — the final decision is recorded in `DECISION_RECORD.md` with rationale.

Without human confirmation, no alignment report is valid and no branch can be selected.

## H. Hard Prohibitions

These rules are absolute and cannot be overridden:

| Prohibition | Reason |
|-------------|--------|
| **No auto-choice** | The evaluator must never select a branch. Selection is a human decision. |
| **No unconfirmed value inference** | Values must come from user-confirmed data only. Inference is invention. |
| **No rubric modification** | The evaluator cannot modify `alters/calibration/rubric.yaml`. Rubric changes require human review (ALT-007). |
| **No calibration update** | The evaluator cannot update calibration scores. Scoring is handled by ALT-007 with human review. |
| **No active alignment files in Phase 0** | No `alignment_*.yaml` files are created. Only the `_template.yaml` exists. |
| **No invented content** | The evaluator must not generate fake user values, branch assessments, or alignment scores. |
