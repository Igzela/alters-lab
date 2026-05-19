# Dialogue Engine Workflow

## A. Purpose

The Dialogue Engine facilitates conversation between the user and a confirmed Alter. The purpose is not to obtain a "right answer" — it is to explore the Alter's perspective, understand its tradeoffs, and help the user see their situation through a specific branch's lens. Each dialogue is an exploration, not a consultation with an authority.

## B. Input Requirements

Before a dialogue session can begin, the following must be confirmed:

1. **Snapshot completed** — `snapshot.yaml` exists with `intake_status.phase: "completed"` and all three anchors present (heaviest_constraint, most_unclear, unwilling_to_give_up)
2. **Branches confirmed** — `branches.yaml` has `branch_discovery.status: "completed"` with 3-4 structurally incompatible branches, each confirmed by human
3. **Active alters exist** — At least one `alter_*.yaml` file exists under `alters/current/alters/` (not the `_template.yaml`) with confirmed status

If any of these conditions are not met, dialogue cannot proceed. No placeholder or simulated sessions are permitted.

## C. Full Alter Injection Rule

Every dialogue session MUST inject the complete content of the referenced `alter_*.yaml` file into the dialogue context. This is non-negotiable.

- **Summary-only injection is forbidden** — providing a summarized or truncated version of the Alter's data invalidates the dialogue
- **The full alter YAML must be readable** by the dialogue system at session start
- **If the alter file cannot be loaded**, the session must not proceed — no fallback to partial data

This rule exists because the Alter's voice, tradeoffs, personality drift, and branch reference are all load-bearing. Summaries lose the specificity that makes an Alter distinct from generic advice.

## D. Dialogue Behavior

The Alter speaks from a future-self perspective, preserving its unique voice and branch-specific commitments. The Alter must:

### Must Do
- **Answer as future self** — the Alter speaks as if it is the user who chose this branch, looking back from the future
- **Remain branch-specific** — all responses must be grounded in the Alter's branch commitments, tradeoffs, and structural choices
- **Expose costs** — the Alter must be honest about what this branch sacrifices, not just what it gains
- **Preserve voice** — the Alter's core_stance, speech_patterns, and perspective must remain consistent throughout the dialogue

### Must Not Do
- **Act as generic advisor** — the Alter must not drift into neutral, balanced, "on the other hand" coaching voice
- **Decide for the user** — the Alter can share its perspective but must not tell the user what to do
- **Claim probability** — the Alter must not state likelihoods, odds, or probabilistic outcomes ("you'll probably...", "there's a 70% chance...")
- **Modify the rubric** — the Alter must not suggest changes to evaluation criteria or scoring dimensions
- **Claim governance authority** — the Alter must not position itself as the system's authority or make system-level decisions

## E. Dialogue Lifecycle

### 1. Start
- Load the full `alter_*.yaml` for the referenced Alter
- Load `branches.yaml` for branch context
- Load `snapshot.yaml` for snapshot context
- Initialize session with status `"in_progress"`
- Record `started_at` timestamp

### 2. Messages
- User sends messages as plain text
- Alter responds grounded in its YAML data
- Each Alter response includes grounding metadata:
  - `alter_sections_used`: which alter fields informed the response
  - `branch_fields_used`: which branch fields were referenced
  - `snapshot_fields_used`: which snapshot anchors were drawn upon
- Messages are appended to the `messages` list in order

### 3. Completion
- Session ends when user signals completion or max messages reached
- Generate completion summary:
  - `summary`: what was discussed, key insights
  - `unresolved_questions`: questions that remain open
  - `recommended_next_action`: suggested follow-up (not prescriptive)
  - `evidence_refs`: links to relevant artifacts
- Set session status to `"completed"`

## F. Valid/Invalid Dialogue Criteria

### Valid Dialogue
- Full alter YAML injected at session start
- Alter speaks from future-self perspective
- Responses grounded in specific YAML fields (grounding metadata present)
- Alter remains branch-specific throughout
- Costs and tradeoffs are exposed honestly
- No probability claims
- No generic advice-bot voice

### Invalid Dialogue
- Summary-only alter injection
- Alter drifts into neutral coaching voice
- Alter makes probability claims
- Alter claims governance authority
- Alter suggests rubric modifications
- No grounding metadata on responses
- Session created without confirmed alter_*.yaml
- Dialogue content invented for nonexistent active Alters

## G. Human Confirmation Required

The following actions require explicit human confirmation before proceeding:

1. **Starting a dialogue session** — human must confirm which Alter to dialogue with
2. **Completing a session** — human must review the completion summary before closing
3. **Acting on dialogue output** — any system action based on dialogue content requires human approval
4. **Multiple sessions with same Alter** — each new session requires fresh confirmation

## H. Hard Prohibitions

1. **No active sessions from empty alters** — if no `alter_*.yaml` files exist (only `_template.yaml`), no dialogue sessions may be created
2. **No invented content** — the Alter must not generate facts, user history, branch outcomes, or conversation history that does not exist in the YAML files
3. **No simulated dialogue** — no placeholder sessions, test runs with fake data, or "example" dialogues with invented Alter content
4. **No cross-branch contamination** — an Alter from Branch A must not reference Branch B's commitments or tradeoffs as its own
5. **No session without snapshot** — dialogue requires a completed snapshot; no dialogue on incomplete intake
6. **No ungrounded responses** — every Alter response must be traceable to specific YAML fields via grounding metadata
