# Branch Discovery Workflow

## A. Purpose

Branch Discovery transforms confirmed snapshot anchors into 3-4 structural, mutually incompatible branches. Each branch represents a fundamentally different way of resolving the core tensions identified in the snapshot. This workflow is the second major phase of the Alters System pipeline, occurring after Snapshot Intake is completed and confirmed.

## B. Input Requirements

Before Branch Discovery can begin, the following must be true:

1. **Snapshot phase is completed**: `alters/current/snapshot.yaml` has `intake_status: "confirmed"`.
2. **All three anchors are non-empty**: `heaviest_constraint`, `most_unclear`, and `unwilling_to_give_up` must contain real user content — not placeholders or empty strings.
3. **Branch discovery status is `not_started`**: No branch generation has been attempted yet.

If any input requirement is not met, Branch Discovery must not proceed.

## C. Pipeline

Branch Discovery follows a three-step pipeline:

### Step 1: Tension Extraction

Extract the core structural tensions from the confirmed snapshot. Tensions are not problems to solve — they are fundamental trade-offs where gaining one thing requires sacrificing another.

- Read `heaviest_constraint` → identifies the binding constraint
- Read `most_unclear` → identifies the deepest uncertainty
- Read `unwilling_to_give_up` → identifies the non-negotiable

Output: a list of 2-4 irreducible tensions.

### Step 2: Structural Branch Identification

For each tension, generate candidate branches that represent distinct structural commitments — not gradations of the same approach.

A valid structural branch:
- Makes an **active choice** (does X, not Y)
- Changes the **1.5-2 year life structure** (not a temporary tweak)
- Is **mutually incompatible** with at least one other branch in the set

An invalid branch:
- Differs only in **result** (same structure, different outcome)
- Differs only in **parameter** (same structure, more/less of something)
- Is a **passive outcome** rather than an active commitment

Output: a candidate list of 4-6 branches.

### Step 3: Convergence

Reduce the candidate list to 3-4 branches that:
1. Are **mutually incompatible** — each pair must conflict on at least one structural dimension.
2. Cover the **full tension space** — together they span the key tensions from Step 1.
3. Pass the **incompatibility test** — for every branch pair (A, B), either A's `incompatible_with` contains B or B's `incompatible_with` contains A.
4. Pass **quality rules** — no result-only differences, no parameter-only differences.

If fewer than 3 branches survive convergence, the snapshot may lack sufficient tension to generate branches. Escalate to human review.

Output: 3-4 final branches recorded in `branches.yaml`.

## D. Valid Branch Criteria

A branch is valid if and only if it meets ALL of the following:

1. **Active structural choice**: The branch commits to a specific path, not a vague aspiration.
2. **Changes 1.5-2yr life structure**: The branch fundamentally restructures how life looks over the next 1.5-2 years.
3. **Incompatible with at least one other branch**: The branch cannot coexist with at least one other branch in the set — choosing it means explicitly NOT choosing another.
4. **Resolves a key tension**: The branch addresses one of the tensions extracted from the snapshot.
5. **Has validation signals**: The branch includes at least one 30-day signal that would confirm or disconfirm it.

## E. Invalid Branch Examples

### Result differences (INVALID)
- "Become a senior engineer" vs "Become a staff engineer" — same structure (corporate career), different outcome level.
- "Earn more money" vs "Earn less money" — same structure, different parameter.

### Parameter differences (INVALID)
- "Work 40 hours/week" vs "Work 60 hours/week" — same structure, different intensity.
- "Freelance full-time" vs "Freelance part-time" — same structure, different commitment level.

### Passive outcomes (INVALID)
- "Things get better" — not a choice, just hope.
- "Find clarity" — not a structural commitment, just an outcome.

## F. Incompatibility Test

Every branch must fill `incompatible_with` with at least one other branch ID. The test is:

```
For each branch B in branches:
  assert len(B.incompatible_with) >= 1
  for each branch_id in B.incompatible_with:
    assert branch_id exists in branches
    assert B.id in branches[branch_id].incompatible_with  # mutual
```

If any branch fails the incompatibility test, it is invalid and must be revised or removed.

## G. Output Format

Branch Discovery produces `alters/current/branches.yaml` with this structure:

```yaml
branch_discovery:
  status: "completed"  # or "not_started" if snapshot not confirmed
  source_snapshot_ref: "alters/current/snapshot.yaml"
  requires_snapshot_phase: "completed"
  pipeline:
    step_1_tension_extraction: { output: [...] }
    step_2_structural_branch_identification: { output: [...] }
    step_3_convergence: { output: [...] }
  quality_rules:
    reject_result_differences: true
    reject_parameter_differences: true
    require_mutual_incompatibility: true
    require_incompatible_with: true
    min_branches: 3
    max_branches: 4

branches:
  - id: "branch-001"
    core_choice: "What this branch fundamentally chooses"
    structural_commitment: "The structural change this commits to"
    key_tension_resolved: "Which tension from Step 1 this resolves"
    incompatible_with: ["branch-002", "branch-003"]
    preserves: ["What this branch keeps from current life"]
    sacrifices: ["What this branch gives up"]
    validation_signal_30d: ["Observable signal within 30 days"]
    invalid_if: ["Condition that would prove this branch wrong"]
  # ... more branches (3-4 total)

branch_template:
  # ... (same as above, for reference)
```

## H. Hard Prohibitions

1. **No branches from empty snapshot**: If `snapshot.yaml` has empty anchors or `intake_status` is not `confirmed`, Branch Discovery must not run.
2. **No invented data**: Every branch must trace back to real snapshot anchors. No fabricated tensions, constraints, or preferences.
3. **No result/parameter-only branches**: Branches must differ in kind, not degree.
4. **No branches before snapshot confirmation**: The pipeline must not be started until the snapshot is confirmed.
5. **No more than 4 branches**: The system cannot handle more than 4 branches. Fewer than 3 means insufficient tension — escalate.
