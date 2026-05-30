# Data Model

All data is stored as YAML/JSON files under `alters/`. No database. Pydantic schemas in `apps/api/src/alters_lab/schemas/` enforce structure and invariants.

## Directory Structure

```
alters/
  current/                    # Active working data (user-specific, gitignored)
    snapshot.yaml             # Current life state
    branches.yaml             # Discovered branches
    reality_trace.yaml        # Reality vs. prediction tracking
    alters/                   # alter_A.yaml through alter_D.yaml
    dialogue/                 # Dialogue session records
    value_alignment/          # Value alignment reports
  sample/                     # Sample data for new users (checked in)
    snapshot.yaml, branches.yaml, alters/, reality_trace.yaml
  calibration/                # Evaluation framework
    rubric.yaml               # 4-axis evaluation rubric
    state.json                # Calibration cycle state
    scores/                   # Per-cycle score records
    rubric_delta_suggestions/ # Rubric evolution suggestions
    checkpoint_plans/         # Checkpoint regeneration plans
  product/                    # Runtime product data
    config/                   # config.yaml, secrets.yaml
    weekly_notes/             # Ingested weekly notes
    weekly_reviews/           # Weekly review sessions
    calibration_records/      # Action alignment scores
    pattern_reviews/          # Behavioral pattern analysis
    behavior_validation/      # Validation reports
    sessions/                 # Provider dialogue sessions
    provider_runs/            # Provider call logs
    exports/                  # Data exports
  archive/                    # Completed cycle archives
```

## Core Entities

### Snapshot (`snapshot.yaml`)

Top-level key: `snapshot:`. Contains the user's current life state.

| Field | Type | Description |
|-------|------|-------------|
| `date` | string \| null | Snapshot date |
| `version` | int | Schema version (>= 1) |
| `anchors` | SnapshotAnchors | Three core anchors |
| `context` | SnapshotContext | Commitments, deadlines, energy |
| `intake_status` | SnapshotIntakeStatus | Phase and completion tracking |
| `evidence_policy` | EvidencePolicy | Source mode and confidence |
| `notes` | list[str] | Freeform notes |

**SnapshotAnchors:**
| Field | Type |
|-------|------|
| `heaviest_constraint` | str |
| `most_unclear` | str |
| `unwilling_to_give_up` | str |

**SnapshotContext:**
| Field | Type |
|-------|------|
| `current_commitments` | list[str] |
| `external_deadlines` | list[str] |
| `energy_state` | str |

**SnapshotIntakeStatus:**
| Field | Type |
|-------|------|
| `phase` | Enum: `not_started`, `asking_heaviest_constraint`, `asking_most_unclear`, `asking_unwilling_to_give_up`, `ready_for_snapshot_confirmation`, `completed` |
| `completed_anchors` | list[AnchorName] |
| `pending_anchor` | AnchorName \| null |

### Branch (`branches.yaml`)

Top-level key: `branch_discovery:` + `branches:`.

**BranchDiscoveryStatus:**
| Field | Type | Description |
|-------|------|-------------|
| `status` | str | `"not_started"` or `"completed"` |
| `source_snapshot_ref` | str | Path to source snapshot |
| `requires_snapshot_phase` | str | Required snapshot phase |
| `confirmed_by` | str | Who confirmed |
| `confirmation_note` | str | Confirmation note |

**Branch:**
| Field | Type | Description |
|-------|------|-------------|
| `id` | str | `branch_A` through `branch_D` |
| `label` | str | Human-readable label |
| `core_choice` | str | The fundamental choice this branch represents |
| `structural_commitment` | str | What must be committed |
| `key_tension_resolved` | str | Which tension this branch resolves |
| `incompatible_with` | list[str] | Other branch IDs this is incompatible with |
| `preserves` | list[str] | What this branch preserves |
| `sacrifices` | list[str] | What this branch sacrifices |
| `validation_signal_30d` | list[str] | Signals to watch in 30 days |
| `invalid_if` | list[str] | Conditions that invalidate this branch |

### Alter (`alters/alter_A.yaml` through `alter_D.yaml`)

| Field | Type | Description |
|-------|------|-------------|
| `id` | str | `alter_A` through `alter_D` (enforced) |
| `branch_ref` | str | Must match: `alter_A` → `branch_A` |
| `label` | str | Alter's name |
| `source_refs` | AlterSourceRefs | References to source files |
| `quality_status` | AlterQualityStatus | Confirmation and active status |
| `voice` | AlterVoice | Personality and stance |

**AlterSourceRefs** (all paths enforced by validator):
| Field | Required Value |
|-------|---------------|
| `snapshot_ref` | `"alters/current/snapshot.yaml"` |
| `branches_ref` | `"alters/current/branches.yaml"` |
| `rubric_ref` | `"alters/calibration/rubric.yaml"` |

**AlterQualityStatus:**
| Field | Type |
|-------|------|
| `human_confirmed` | bool (must be `true`) |
| `active` | bool (must be `true`) |
| `notes` | list[str] |

**AlterVoice:**
| Field | Type |
|-------|------|
| `core_stance` | str (must be non-empty) |
| `typical_concern` | str |
| `decision_style` | str |
| `self_warning` | str |

### Rubric (`calibration/rubric.yaml`)

4-axis evaluation framework. `auto_modify` is always `false`.

### RealityTrace (`current/reality_trace.yaml`)

Tracks how reality diverges from branch predictions over time.

### ActionAlignmentScore (`product/calibration_records/`)

Weekly review scoring: direction alignment, execution consistency, avoidance level, verdict label.

### WeeklyReviewSession (`product/weekly_reviews/`)

Complete weekly review session with review note, dialogue summary, primary correction, supporting actions.

### WeeklyNoteExtractedRecord (`product/weekly_notes/`)

Ingested and parsed weekly note from Obsidian. Stores the raw note and extracted structured fields.

| Field | Type | Description |
|-------|------|-------------|
| `record_id` | str | Unique identifier |
| `source_type` | Literal["obsidian_weekly_note"] | Always this value |
| `raw_note_preserved` | Literal[True] | Raw note is preserved |
| `derived_from_raw_note` | Literal[True] | Record is derived from raw note |
| `source_path` | str \| null | Original file path |
| `raw_note` | str | Original raw note text |
| `session_type` | SessionType | One of: `personal`, `project`, `learning`, `relationship` |
| `observable_facts` | list[str] | 5-7 extracted facts |
| `subjective_state` | str | How the user feels |
| `primary_problem` | str | Main issue identified |
| `friction_or_avoidance_point` | str | What's being avoided |
| `desired_correction` | str | What the user wants to change |
| `extraction_warnings` | list[str] | Warnings from extraction |
| `edit_history` | list[WeeklyNoteEditDiff] | History of edits |
| `created_at` | str | Creation timestamp |
| `updated_at` | str \| null | Last update timestamp |

### ProviderConfig (`product/config/config.yaml`)

Provider configuration for LLM integration. Controls mode, endpoint, model, and safety flags.

| Field | Type | Description |
|-------|------|-------------|
| `mode` | ProviderMode | `disabled`, `mock`, or `openai-compatible-http` |
| `base_url` | str \| null | API endpoint URL |
| `model` | str \| null | Model name |
| `timeout_seconds` | int | Request timeout (1-600) |
| `secret_storage` | SecretStorage | `keyring` or `secrets_yaml_fallback` |
| `key_name` | str | Keyring key name |

**ProviderSafetyFlags** (returned in status responses):
| Field | Type | Description |
|-------|------|-------------|
| `provider_output_persists_by_default` | Literal[False] | Output persistence disabled |
| `provider_output_can_write_active_yaml` | Literal[False] | Cannot modify active YAML |
| `provider_output_can_generate_reality_score` | Literal[False] | Cannot generate scores |
| `behavior_validated` | Literal[False] | Behavior not yet validated |
| `p6_sealed` | Literal[False] | P6 not yet sealed |

### PatternReviewRecord (`product/pattern_reviews/`)

Four-week pattern review analyzing behavioral patterns across multiple weeks.

| Field | Type | Description |
|-------|------|-------------|
| `review_id` | str | Unique identifier |
| `status` | Literal["insufficient_data", "no_pattern", "pattern_triggered"] | Review outcome |
| `weeks_evaluated` | int | Number of weeks analyzed |
| `triggered_patterns` | list[TriggeredPattern] | Patterns that were triggered |
| `created_at` | str | Creation timestamp |
| `active_yaml_modified` | bool | Whether active YAML was modified |
| `provider_called` | bool | Whether provider was called |

**TriggeredPattern:**
| Field | Type | Description |
|-------|------|-------------|
| `pattern` | PatternName | Pattern identifier |
| `occurrences` | int | Number of occurrences |
| `confidence` | float | Confidence score (0-1) |
| `strategy_constraint` | str | Constraint for this pattern |

**PatternName** values:
- `repeated_noisy_progress`
- `repeated_avoidance_disguised_as_work`
- `repeated_sleep_breakdown`
- `repeated_over_scope`
- `repeated_action_mismatch`
- `repeated_primary_correction_failure`

## Key Invariants

- **extra="forbid"**: Most Pydantic models reject unknown fields. YAML files on disk may have extra fields, but API validation is strict.
- **Alter IDs**: Must be exactly `alter_A`, `alter_B`, `alter_C`, `alter_D`.
- **Branch refs**: `alter_A` must reference `branch_A`, etc.
- **Source refs**: Must point to exact paths (`alters/current/snapshot.yaml`, etc.).
- **Completion validation**: Completed snapshots require all three anchors filled and `pending_anchor: null`. Completed branch discovery requires exactly 4 branches.
- **Mutual incompatibility**: Each branch must have non-empty `incompatible_with` listing the other 3 branch IDs.
- **Rubric immutability**: `auto_modify` is always `false`. Rubric changes require explicit human approval.
- **Approval tokens**: Write operations require an `approval_token` — a domain-specific safety gate, not HTTP auth.
