> **Note**: This is a historical design document. Phase references (Phase 0, P4) reflect the system's state at time of writing. For current status, see CLAUDE.md.

# Alter Generation Workflow

## A. Purpose

Alter Generation transforms each human-confirmed branch into one Alter — a coherent 1.5-2 year future self rooted in that branch's structural commitment. Each Alter is not a prediction; it is a grounded projection of what life could look like if the user commits to that branch's path. One branch produces exactly one Alter.

## B. Input Requirements

Before Alter Generation can begin, the following must be true:

1. **Snapshot phase is completed**: `alters/current/snapshot.yaml` has `intake_status: "completed"`.
2. **Branch Discovery is completed**: `alters/current/branches.yaml` has `branch_discovery.status: "completed"` and the branches list contains 3-4 entries.
3. **All branches are human-confirmed**: Each branch has been reviewed and confirmed by the human user. The system must not generate Alters from unconfirmed branches.
4. **Rubric exists**: `alters/calibration/rubric.yaml` is present and contains valid dimensions for personality drift assessment.

If any input requirement is not met, Alter Generation must not proceed.

## C. Generation Pipeline

Alter Generation follows a four-step pipeline per branch:

### Step 1: Structural Commitment → Life State

Read the branch's `structural_commitment`, `preserves`, and `sacrifices`. Translate these into concrete life state projections:

- `location_or_environment`: Where does this person live and work?
- `daily_structure`: What does a typical day look like?
- `primary_tension`: What is the central tension in this life?
- `social_context`: Who are the key people and relationships?
- `dominant_environment`: What is the dominant physical/social environment?

### Step 2: Key Tension → Tradeoffs

Read the branch's `key_tension_resolved`. Identify what is gained and what is lost by committing to this path:

- `tradeoffs.gained`: Concrete things this branch provides (skills, relationships, experiences, stability).
- `tradeoffs.lost`: Concrete things this branch sacrifices (alternative paths, opportunities, aspects of current life).
- `skills_trajectory.accelerated`: What skills grow fastest in this life.
- `skills_trajectory.stagnated`: What skills atrophy or plateau.

### Step 3: Personality Drift via Rubric Bias Correction

Apply the rubric to estimate how personality dimensions shift under this branch's structural commitment. For each dimension:

- `execution_discipline`: Does this branch demand more or less structure?
- `exploration_freedom`: Does this branch open or close exploration?
- `identity_stability`: Does this branch stabilize or destabilize identity?
- `risk_tolerance`: Does this branch increase or decrease risk appetite?
- `engineering_closure`: Does this branch push toward completion or leave things open?

Each dimension gets a `direction` (increase/decrease/stable) and a `reason` tied to the structural commitment.

### Step 4: Voice Generation

The Alter's voice is not a personality quiz result — it is a perspective rooted in the structural commitments of the branch. Generate:

- `core_stance`: The fundamental orientation toward the world in this life.
- `typical_concern`: What keeps this person up at night.
- `decision_style`: How this person makes choices.
- `self_warning`: What this person would warn their past self about.

## D. Valid and Invalid Alter Criteria

### A valid Alter MUST:

1. Have a `branch_ref` pointing to a confirmed branch.
2. Have a `snapshot_ref` pointing to the current snapshot.
3. Have a `time_horizon` of "1.5-2年后".
4. Have a `voice` with non-empty `core_stance`, `typical_concern`, `decision_style`, and `self_warning`.
5. Have non-empty `source_branch.core_choice` and `source_branch.structural_commitment`.
6. Have concrete `tradeoffs` (not empty gained/lost lists).
7. Be grounded in real snapshot anchors — no invented user facts.

### An invalid Alter:

1. Predicts probability ("70% chance you'll succeed") — this is forbidden.
2. Gives neutral, generic advice ("be yourself", "follow your heart") — this is a bot, not an Alter.
3. Has no branch_ref — it is untethered.
4. Has empty voice fields — it has no perspective.
5. Is generated from a branch that was not human-confirmed.
6. Contains invented user facts not present in the snapshot.

## E. Human Confirmation Required

Alter Generation in Phase 0 is a documentation-only process. The template (`_template.yaml`) defines the structure. Active `alter_*.yaml` files must NOT be created until:

1. All branches are human-confirmed (not just generated).
2. The human explicitly authorizes Alter generation for confirmed branches.
3. The generated Alters are reviewed by the human before becoming active.

The system must not generate active Alters from empty or unconfirmed branches.

## F. Output Format

Alter Generation produces `alter_*.yaml` files in `alters/current/alters/`, one per confirmed branch:

```
alters/current/alters/
├── _template.yaml          # inactive template (Phase 0)
├── alter_branch-001.yaml   # active Alter for branch-001 (requires human confirmation)
├── alter_branch-002.yaml   # active Alter for branch-002
└── alter_branch-003.yaml   # active Alter for branch-003
```

Each `alter_*.yaml` follows the structure defined in `_template.yaml`, with all fields populated from the generation pipeline.

## G. Hard Prohibitions

1. **No generation from empty branches**: If `branches.yaml` has an empty branches list or `branch_discovery.status` is not "completed", Alter Generation must not run.
2. **No generation from unconfirmed branches**: Only human-confirmed branches produce Alters.
3. **No invented user facts**: Every Alter field must trace back to real snapshot anchors or branch definitions. No fabricated constraints, preferences, or life circumstances.
4. **No probability prediction**: Alters do not predict outcomes. They project possibilities.
5. **No neutral advice bot**: An Alter with generic, non-committal voice is invalid. Each Alter must have a distinct, committed perspective.
6. **No active alter files in Phase 0**: Only `_template.yaml` exists until human confirmation authorizes active generation.
