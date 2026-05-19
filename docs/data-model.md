# Data Model

## Entities

### Snapshot

| Field | Type | Description |
|-------|------|-------------|
| id | string | Identifier |
| heaviest_constraint | text | The biggest constraint currently shaping decisions |
| most_unclear | text | The most uncertain direction or question |
| unwilling_to_give_up | list[str] | Things you will not sacrifice regardless of branch |
| captured_at | datetime | When the snapshot was taken |
| cycle | int | Which calibration cycle this belongs to |

### Branch

| Field | Type | Description |
|-------|------|-------------|
| id | string | Identifier |
| snapshot_id | string | FK to Snapshot |
| name | string | Branch label |
| description | text | What this path looks like |
| structural_difference | text | How this differs from other branches in kind, not degree |
| tradeoffs | list[str] | What you gain and lose on this path |
| created_at | datetime | Creation timestamp |

### Alter

| Field | Type | Description |
|-------|------|-------------|
| id | string | Identifier |
| branch_id | string | FK to Branch |
| name | string | Alter's name or label |
| values | list[str] | Core values on this branch |
| narrative | text | Coherent life story for this path |
| tradeoffs | list[str] | What this Alter has accepted or sacrificed |
| created_at | datetime | Creation timestamp |

### RealityTrace

| Field | Type | Description |
|-------|------|-------------|
| id | string | Identifier |
| branch_id | string | FK to Branch |
| observed_at | datetime | When this observation was recorded |
| divergence | text | How reality differs from predicted branch |
| delta_magnitude | float | How far reality has drifted (0-1) |
| notes | text | Additional context |

### RealityScore

| Field | Type | Description |
|-------|------|-------------|
| id | string | Identifier |
| cycle | int | Calibration cycle |
| branch_id | string | FK to Branch |
| scores | JSON | Per-dimension scores |
| total_score | float | Weighted total |
| scored_at | datetime | When scored |

### Rubric

| Field | Type | Description |
|-------|------|-------------|
| id | string | Identifier |
| version | int | Version number |
| dimensions | list[RubricDimension] | Evaluation dimensions |
| auto_modify | bool | Whether rubric can self-modify (always false) |
| created_at | datetime | Creation timestamp |

### RubricDimension

| Field | Type | Description |
|-------|------|-------------|
| name | string | Dimension identifier |
| description | text | What this dimension measures |
| weight | float | Relative weight (0-1) |
| scale | string | Scoring scale description |

### Archive

| Field | Type | Description |
|-------|------|-------------|
| id | string | Identifier |
| cycle | int | Completed cycle number |
| snapshot_snapshot | Snapshot | Archived snapshot |
| branches | list[Branch] | Archived branches |
| scores | list[RealityScore] | Archived scores |
| reality_traces | list[RealityTrace] | Archived traces |
| archived_at | datetime | When archived |

## Relationships

- Snapshot 1:N Branch
- Branch 1:N Alter
- Branch 1:N RealityTrace
- Branch 1:N RealityScore
- Snapshot 1:1 Archive (per cycle)

## Invariants

- Branches must be structurally and mutually incompatible (not gradations)
- Alter must reference a valid branch_ref
- Time horizon for branches is fixed at 1.5-2 years
- Dialogue must inject full alter.yaml content
- Rubric auto_modify is always false
- Any unknown_error requires human review
