# Snapshot Intake Workflow

## A. Purpose — Three State Anchors

The intake workflow captures three state anchors that define the user's current position:

1. **heaviest_constraint** — The biggest constraint currently shaping decisions. The weight everything else must work around.
2. **most_unclear** — The most uncertain direction or question. The branch point — the thing that could go multiple ways.
3. **unwilling_to_give_up** — Non-negotiable anchors. Things that will NOT be sacrificed regardless of which branch is taken.

These three anchors are the minimum viable input for branch discovery. Nothing else is required before branches can be generated.

## B. Design Principles

1. **Ask "what is pulling you"** — not "what do you want". The system surfaces tensions, not preferences.
2. **One question at a time** — never ask multiple questions in a single prompt. Each anchor gets its own focused exchange.
3. **Wait for a complete answer** — do not advance to the next anchor until the current one has a substantive response. Silence or deflection is not a complete answer.
4. **No leading** — do not suggest answers. Provide context and examples only as fallback when the user is stuck.

## C. Intake State Machine

```
not_started
    |
    v
asking_heaviest_constraint
    |
    v
asking_most_unclear
    |
    v
asking_unwilling_to_give_up
    |
    v
ready_for_snapshot_confirmation
    |
    v
completed
```

Transitions are triggered by substantive answers to each anchor question. The state machine cannot skip steps or go backwards.

## D. Required Questions

### Anchor 1: heaviest_constraint

**Primary question:**
> What is the heaviest constraint currently shaping your decisions?

**What counts as a complete answer:** A specific, concrete constraint — not a vague direction. Examples: a deadline, a financial obligation, a relationship, a health condition, a contractual commitment.

### Anchor 2: most_unclear

**Primary question:**
> What is the most unclear or uncertain direction in your life right now?

**What counts as a complete answer:** A specific fork or uncertainty — not a general feeling of confusion. Examples: "whether to stay in my role or take the offer", "whether to move cities", "whether to commit to this project or pivot".

### Anchor 3: unwilling_to_give_up

**Primary question:**
> What are you unwilling to give up, no matter which direction things go?

**What counts as a complete answer:** One or more specific, concrete things. Not abstract values. Examples: "weekends with my kids", "working on something technically challenging", "living in a walkable neighbourhood".

## E. Guided Fallback Prompts

Use these only when the user is stuck or gives an incomplete answer. Do not read through the entire list — pick the most relevant category and offer 1-2 prompts.

### Constraint categories (for heaviest_constraint)

- **Time** — "Is there a deadline or time pressure shaping your choices?"
- **Path** — "Is there a commitment that locks you into a particular direction?"
- **Execution** — "Is there something you're responsible for delivering right now?"
- **Resource** — "Is there a financial or material constraint limiting your options?"
- **Energy** — "Is there something draining your capacity that constrains what else you can take on?"
- **Relationship** — "Is there a relationship or obligation to another person that limits your freedom?"

### Uncertainty categories (for most_unclear)

- **Education** — "Are you uncertain about whether to learn something new or go deeper on what you know?"
- **Technical** — "Are you uncertain about which technical direction to commit to?"
- **Career** — "Are you uncertain about your professional direction?"
- **Relationship** — "Are you uncertain about the direction of a relationship?"
- **Identity** — "Are you uncertain about who you want to become?"
- **Autonomy** — "Are you uncertain about how much independence you want versus stability?"

### Value categories (for unwilling_to_give_up)

- **Autonomy** — "Is independence or self-direction non-negotiable for you?"
- **Technical** — "Is working on technically interesting problems non-negotiable?"
- **Engineering** — "Is the craft of building things non-negotiable?"
- **Stable** — "Is stability or predictability non-negotiable?"
- **Relationships** — "Are certain relationships non-negotiable?"
- **Health** — "Is your physical or mental health non-negotiable?"

## F. Snapshot Confirmation

After all three anchors are answered, the system must:

1. **Show the full proposed snapshot.yaml** — the complete file contents, not a summary.
2. **Ask for explicit confirmation** — "Does this look right? Any corrections before I lock it in?"
3. **Wait for confirmation** — do not proceed to branch discovery until the user confirms.
4. **If corrections are requested** — update the relevant anchor(s) and re-show the full snapshot.

The snapshot is only marked `completed` after explicit user confirmation.

## G. Hard Prohibitions

1. **No branches before confirmation** — branch discovery must not begin until the snapshot is confirmed.
2. **No alters during intake** — no alter generation, no alter templates, no alter-related file creation during intake.
3. **No multiple questions at once** — one question per exchange, always.
4. **No invented data** — empty fields stay empty. Do not fill in placeholder or example content on behalf of the user.

## H. Output Artifact

The only output of the intake workflow is:

```
alters/current/snapshot.yaml
```

No other files are created, modified, or referenced during intake.
