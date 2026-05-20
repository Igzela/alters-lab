# P6-000: Personal Long-Term Use Hardening Plan

**Date**: 2026-05-20
**Status**: done
**Phase**: P6
**Primary goal**: Personal Long-Term Use Hardening
**Not primary goal**: Public productization

## 1. Identity and Scope

P6 is validated by actual usage, not code completion alone. P6 produces two milestone states:

- `P6_CODE_COMPLETE` — all runtime milestones implemented.
- `P6_BEHAVIOR_VALIDATED` — only after 4 weeks of real-use validation window.

P6 is NOT public productization. P6 hardens the system for Charlie's personal long-term use.

## 2. Usage Cadence

- Weekly deep review.
- 1-2 sessions per week.
- 30-60 minutes each.

## 3. Review Scope

- Mixed domain review.
- One session, one primary `session_type`.
- Allowed session types: `personal`, `project`, `learning`, `relationship`.

## 4. Output Model

Two-layer output:
- `review_note` — human-readable review.
- `calibration_record` — machine-readable calibration record.

## 5. Primary Metric

`action_alignment` — whether actions match the user's endorsed direction.

## 6. Scoring Model

Three-dimensional score with required evidence:

| Dimension | Range | Meaning |
|-----------|-------|---------|
| `direction_alignment` | 0.0-1.0 | How well direction matches endorsed goals |
| `execution_consistency` | 0.0-1.0 | How consistently execution follows direction |
| `avoidance_level` | 0.0-1.0 | Higher means stronger avoidance |

Required evidence per session:
- `one_action_evidence`
- `one_avoidance_or_friction_evidence`
- `one_next_correction`

## 7. Next Action Rule

- Exactly one required `primary_next_correction`.
- Optional 0-2 `supporting_actions`.
- Supporting actions must serve the primary correction, not create new fronts.

## 8. Failure Review

Combine direct accountability and short diagnosis.

Status values: `completed`, `partial`, `not_completed`.

If `partial` or `not_completed`:
1. Mark failure honestly.
2. Diagnose in max 3 sentences.

Failure categories:
- `scope_too_large`
- `emotional_resistance`
- `environment_blocker`
- `goal_not_real`
- `strategy_wrong`
- `energy_or_health_limit`
- `priority_conflict`

Required next move:
- `shrink`
- `retry`
- `replace`
- `pause_with_reason`

## 9. Self-Deception Tracking

Mode: `lightweight_plus`.

Required field: `self_deception_risk` — `low` | `medium` | `high`.

If `medium` or `high`, require:
- `rationalization_pattern`
- `evidence` (max 2 sentences)
- `avoided_truth` (max 1 sentence)

Rationalization patterns:
- `over_analysis`
- `avoidance_disguised_as_strategy`
- `moral_superiority`
- `productivity_theatre`
- `emotional_minimization`
- `false_urgency`
- `dependency_on_external_validation`
- `other`

Forbidden:
- No shadow diagnosis.
- No personality judgment.
- No unsupported motive guessing.

## 10. Alter Challenge Mode

Default: evidence-based gentle challenge.
Escalation: limited strong challenge.

Strong challenge allowed ONLY when:
- `self_deception_risk` is `high`.
- Action evidence is weak.
- Explanation contradicts behavior.

Hard limits:
- Max one strong challenge per session.
- Must cite concrete action evidence.
- No personality judgment.

## 11. Alter Selection

- System recommends optimal alter.
- User can override.
- Override requires reason.
- "Optimal" must NOT mean most comfortable.

Factors:
- `session_type_match`
- `unresolved_drift_match`
- `challenge_value`
- `action_alignment_relevance`
- `overuse_penalty`

## 12. Counter-Alter

Mode: primary alter plus optional counter-alter.
Default: one primary alter.

Counter-alter allowed when:
- `decision_conflict_high`
- `self_deception_risk_medium_or_high`
- `repeated_failure_same_category`
- `user_requests_deeper_review`

Counter-alter is for exposing conflict, not debate performance.

## 13. Weekly Review Flow

1. `structured_prefill`
2. System recommends primary alter
3. Optional counter-alter
4. Alter dialogue
5. Evidence-based challenge if needed
6. `review_note`
7. `calibration_record`
8. `next_week_primary_correction`

## 14. Prefill Fields

### observable_facts
- Max 7.
- Only observable facts, no interpretation.

### subjective_state
- Max 3 sentences.
- Real feelings allowed, but not packaged as facts.

### primary_problem
- Exactly one.

### friction_or_avoidance_point
- Exactly one.

## 15. Reality Verdict

Mode: label plus one-sentence verdict.

Labels:
- `aligned_progress`
- `noisy_progress`
- `avoidance_disguised_as_work`
- `recovery_week`
- `unstable_but_useful`
- `blocked_by_environment`

## 16. Verdict Calibration

Side-by-side comparison:
- `user_verdict`
- `system_verdict`
- `discrepancy_note`

Purpose: compare user's self-judgment against evidence.

## 17. Pattern Review

Every 4 weeks. Detect:
- `repeated_noisy_progress`
- `repeated_avoidance_disguised_as_work`
- `repeated_sleep_breakdown`
- `repeated_over_scope`
- `repeated_action_mismatch`
- `repeated_primary_correction_failure`

## 18. Pattern Response

Reminder plus strategy constraint.

Trigger: same negative pattern appears at least 3 times in last 4 weeks, high confidence required.

Response:
1. Identify repeated pattern.
2. Impose strategy constraint.
3. Next week primary correction must reflect the constraint.

## 19. Evidence Source Policy

Semi-automatic evidence.
- First evidence source: Obsidian weekly note.
- Later source: GitHub.
- System extracts candidate evidence.
- User confirms what enters weekly review.

## 20. Obsidian Weekly Note Flow

Hybrid flow:
1. User writes raw weekly note first.
2. System extracts structure.
3. System asks gap questions.
4. System challenges evidence.
5. System generates `review_note` + `calibration_record`.

Hard rule: system cannot invent weekly facts.

## 21. Raw Weekly Note Template

Medium template.

Required:
- 5-7 observable facts.
- Max 3 subjective state sentences.
- 1 primary problem.
- 1 friction or avoidance point.

```markdown
# Weekly Review - YYYY-MM-DD

## Session Type
personal / project / learning / relationship

## Observable Facts
-
-
-
-
-

## Subjective State
1-3 sentences.

## Primary Problem
One sentence.

## Friction / Avoidance
One concrete friction or avoidance point.

## Desired Correction
One primary correction for next week.
```

## 22. Extraction Edit Policy

- Raw note preserved.
- Extracted record editable.
- Edit diff required.
- `correction_note` required for meaningful semantic edits.

## 23. Extraction Edit Challenge

Only challenge major edits.

Triggers:
- Deleting negative facts.
- Lowering `self_deception_risk`.
- Changing failure status.
- Lowering `avoidance_level`.

Challenge question: "这是事实修正，还是叙事软化？"

## 24. Provider Policy

- Real provider allowed.
- Default: disabled or mock.
- Activation: explicit user configuration only.
- No API key committed.
- No default real provider calls.
- Weekly review must run with mock.
- Real provider output cannot auto-write active YAML.
- Real provider output cannot auto-generate reality score.

## 25. Data Retention

- Default long-term save.
- Manual delete/export/archive required.
- Reason: preserve long-term pattern value while retaining user exit rights.

## 26. Source of Truth

Dual-layer truth:
- Primary evidence: Obsidian raw weekly note.
- Derived record: system calibration record.

Conflict resolution:
- Raw note + edit diff wins.
- Calibration record must mark `derived_from_raw_note`.
- Human edits require `correction_note`.

## 27. Reminder

- Fixed weekly reminder with skip reason.
- `skip_allowed`: true.
- `skip_requires_reason`: true.

## 28. Success Standard

P6 success is behavior change, not feature completion.

Criteria:
- `action_alignment_score_improves`
- `repeated_negative_patterns_reduce`
- `primary_correction_completion_rate_improves`

## 29. Validation Window

4 weeks.

Required before P6 can be sealed:
- 4 weekly reviews.
- At least 4 calibration records.
- At least 1 monthly pattern review.
- Measurable change in action alignment / negative patterns / primary correction completion.

## 30. No-Improvement Policy

If no behavior improvement after 4 weeks:
1. First audit usage integrity.

Usage integrity checks:
- Weekly notes completed honestly.
- Calibration records created.
- Primary corrections set.
- Failure reviews honest.
- `self_deception_risk` not softened.
- Sessions not skipped too often.

If usage invalid:
- Fix usage behavior, do not add features.

If usage valid but no improvement:
- Decide redesign or stop expansion.

---

## P6 Milestone Plan

| ID | Title | Status | Depends On |
|----|-------|--------|------------|
| P6-000 | Personal Long-Term Use Hardening Plan | done | P5-CLOSEOUT |
| P6-M1 | Obsidian Weekly Note Ingest | ready_with_approval | P6-000 |
| P6-M2 | Weekly Review Session Runtime | blocked | P6-M1 |
| P6-M3 | Action Alignment Scoring | blocked | P6-M2 |
| P6-M4 | Self-Deception and Challenge Layer | blocked | P6-M3 |
| P6-M5 | Alter Recommendation Engine | blocked | P6-M2 |
| P6-M6 | Reminder / Skip-with-Reason Flow | blocked | P6-M2 |
| P6-M7 | 4-Week Pattern Review | blocked | P6-M3 |
| P6-M8 | Data Retention / Export / Delete | blocked | P6-M2 |
| P6-M9 | Real Provider Optional Enablement | blocked | P6-M2 |
| P6-M10 | Behavior Validation Gate | blocked | P6-M1 through P6-M9 |
| P6-M11 | P6 Closeout | blocked | P6-M10 |

### P6-M1: Obsidian Weekly Note Ingest

- Parse semi-fixed weekly note.
- Preserve raw note.
- Produce editable extracted record.

### P6-M2: Weekly Review Session Runtime

- Structured prefill -> alter recommendation -> dialogue -> review_note + calibration_record.

### P6-M3: Action Alignment Scoring

- Implement `direction_alignment`, `execution_consistency`, `avoidance_level`.
- Evidence requirements.
- Next correction rule.

### P6-M4: Self-Deception and Challenge Layer

- Implement `self_deception_risk`, `rationalization_pattern`.
- Evidence-based challenge.
- Edit challenge.

### P6-M5: Alter Recommendation Engine

- Recommend primary alter and optional counter-alter.
- Use defined factors: session_type_match, unresolved_drift_match, challenge_value, action_alignment_relevance, overuse_penalty.

### P6-M6: Reminder / Skip-with-Reason Flow

- Weekly reminder state.
- Skip reason record.

### P6-M7: 4-Week Pattern Review

- Detect repeated patterns.
- Impose strategy constraints when threshold met (3+ occurrences in 4 weeks).

### P6-M8: Data Retention / Export / Delete

- Manual delete, export, archive controls for weekly review records.

### P6-M9: Real Provider Optional Enablement

- Provider remains disabled/mock by default.
- Explicit configuration only.
- No auto-mutation.

### P6-M10: Behavior Validation Gate

After 4 weeks, judge P6 as:
- `P6_BEHAVIOR_VALIDATED`
- `P6_FAILED_TO_VALIDATE`
- `P6_USAGE_INVALID`

### P6-M11: P6 Closeout

Only seal P6 if behavior validation passes.
