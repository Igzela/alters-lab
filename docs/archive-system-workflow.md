> **Note**: This is a historical design document. Phase references (Phase 0, P4) reflect the system's state at time of writing. For current status, see CLAUDE.md.

# Archive System Workflow

## A. Purpose

The Archive System preserves historical system states at meaningful checkpoints. Each archive captures a complete snapshot of the system at a point in time — branches, alters, scores, reality traces, and resolution — so that past decisions and states can be reviewed, compared, and learned from.

Archives are read-only records. Once created, archive contents must never be modified.

## B. Input Requirements

An archive may be created when one or more of the following conditions is met:

- **Branch resolution**: A branch has been fully evaluated (chosen, rejected, or declared stale) and the cycle is complete.
- **Major event**: A significant life event has occurred that changes the system state fundamentally (new constraint, constraint removed, energy shift).
- **Natural checkpoint**: A scheduled calibration checkpoint has been completed and results are available.
- **Human request**: The user explicitly requests an archive of the current state.

An archive cannot be created if:
- No snapshot exists or the snapshot is incomplete
- No branches exist
- The system is in an intermediate state (intake in progress, branch discovery running, dialogue active)

## C. Folder Naming Convention

Each archive is stored in `alters/archive/YYYY-MM-DD_event/` where:

- `YYYY-MM-DD` is the date of the archive
- `event` is a short slug describing the trigger event (e.g., `branch-resolved`, `major-event`, `checkpoint-complete`, `manual`)

Examples:
- `alters/archive/2026-05-20_branch-resolved/`
- `alters/archive/2026-06-01_major-event/`
- `alters/archive/2026-06-15_checkpoint-complete/`

## D. Archive Contents

Each archive folder contains the following files:

| File | Description |
|------|-------------|
| `snapshot.yaml` | Copy of `alters/current/snapshot.yaml` at archive time |
| `branches.yaml` | Copy of `alters/current/branches.yaml` at archive time |
| `reality_trace.yaml` | Reality trace events recorded for this cycle |
| `reality_score.yaml` | Calibration scores for this cycle (if checkpoints exist) |
| `resolution.yaml` | Resolution record: what happened, what was chosen, outcome |
| `rubric_delta.yaml` | Optional rubric delta proposal (null unless human proposes changes) |
| `alters/` | Folder containing copies of `alter_*.yaml` files relevant to this archive |

## E. Archive Triggers

| Trigger | When | What is archived |
|---------|------|-----------------|
| Branch resolved | User confirms branch choice or rejection | Full state snapshot + resolution |
| Major event | New constraint, constraint removed, energy shift | Full state snapshot + resolution (event_description) |
| Checkpoint complete | Calibration checkpoint after baseline established | Score + trace + resolution (if branch resolved) |
| Human request | User says "archive this" or "save this state" | Full state snapshot + resolution (manual) |

## F. Archive Process

1. **Validate preconditions**: Confirm snapshot exists, branches exist, no active intake/discovery/dialogue session is running.
2. **Copy current state**: Create archive folder with date-event name. Copy snapshot.yaml, branches.yaml, alter_*.yaml files into the archive.
3. **Create resolution**: Write resolution.yaml recording what happened in this cycle — which branches were evaluated, what was chosen (if any), and the outcome.
4. **Copy reality trace**: If reality trace events exist for this cycle, copy them into reality_trace.yaml.
5. **Copy calibration scores**: If calibration scores exist for this cycle, copy them into reality_score.yaml.
6. **Propose rubric delta** (optional): If drift observations suggest rubric changes, create rubric_delta.yaml with a proposal. Set `reject_auto_apply: true`. The proposal is inactive until human confirms it.
7. **Verify archive**: Confirm all files exist, no fields were modified, archive_id matches folder name.

## G. Valid / Invalid Patterns

### Valid
- Archive created after branch resolution with full state copy
- Archive created on human request with full state copy
- Archive folder name matches archive_id in all files
- All archive files are faithful copies of current state
- rubric_delta.yaml has proposal: null (no auto-proposals)
- Resolution references real branches that existed in this cycle

### Invalid
- Archive created before snapshot is complete
- Archive created without branches
- Archive created during active intake or branch discovery
- Archive files contain modified fields (not faithful copies)
- Archive folder name does not match archive_id
- rubric_delta applied without human confirmation
- Resolution references branches that did not exist
- Real dated archive folders created in Phase 0 (no active cycles exist)

## H. Rubric Delta Policy

Rubric deltas within archives follow strict rules:

- **Proposal only**: rubric_delta.yaml contains a proposal, never an applied change.
- **reject_auto_apply: true**: This field is always true. No exceptions.
- **Human confirmation required**: The proposal sits inactive until the human explicitly confirms the change.
- **Decision record required**: Every rubric change requires a linked decision record explaining why.
- **No auto-regenerate**: The rubric is never automatically regenerated or updated based on drift observations alone.

## I. Hard Prohibitions

1. **No auto-apply**: Rubric deltas cannot be applied automatically. `reject_auto_apply: true` is permanent.
2. **No auto-regenerate**: The rubric is never automatically regenerated.
3. **No invent facts**: Archive contents are faithful copies of current state. No fields are invented, assumed, or filled in.
4. **No modification after archival**: Once archived, contents are read-only. No post-archival edits.
5. **No real archives in Phase 0**: No real dated archive folders (e.g., `alters/archive/2026-05-19_*`) may be created until active cycles exist.
6. **No archive during active operations**: Archives cannot be created while intake, branch discovery, or dialogue is in progress.
7. **No rubric modification**: The archive system cannot modify the rubric. It can only propose changes that require human confirmation.
