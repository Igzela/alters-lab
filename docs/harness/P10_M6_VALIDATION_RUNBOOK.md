# P10-M6: Validation Runbook

**Created:** 2026-05-28
**P6 State:** CODE_COMPLETE / VALIDATION_IN_PROGRESS / NOT_SEALED

## Validation Window

- **Start date:** 2026-05-28
- **Required duration:** 21 days / 4 ISO weeks
- **Required completion:** 4 weekly reviews, 4 calibration records, 1 pattern review

## Weekly Cycle Protocol

### 1. Ingest Weekly Note

```bash
curl -s -X POST http://127.0.0.1:18790/obsidian-weekly-note/ingest \
  -H "Content-Type: application/json" \
  -d '{"raw_note": "## Session Type\n<type>\n\n## Observable Facts\n<facts>\n\n## Subjective State\n<state>\n\n## Primary Problem\n<problem>\n\n## Friction / Avoidance\n<friction>\n\n## Desired Correction\n<correction>"}'
```

Valid session types: `personal`, `project`, `learning`, `relationship`

### 2. Start Weekly Review

```bash
curl -s -X POST http://127.0.0.1:18790/weekly-review/start \
  -H "Content-Type: application/json" \
  -d '{"weekly_note_record_id": "<record_id_from_step_1>"}'
```

### 3. Complete Weekly Review

```bash
curl -s -X POST http://127.0.0.1:18790/weekly-review/<session_id>/complete \
  -H "Content-Type: application/json" \
  -d '{
    "review_note": "<review note>",
    "dialogue_summary": "<summary>",
    "primary_next_correction": "<correction>",
    "supporting_actions": ["<action1>", "<action2>"],
    "calibration_record_shell": {}
  }'
```

### 4. Create Action Alignment Score

```bash
curl -s -X POST http://127.0.0.1:18790/action-alignment/score \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "<session_id_from_step_2>",
    "scores": {
      "direction_alignment": <0.0-1.0>,
      "execution_consistency": <0.0-1.0>,
      "avoidance_level": <0.0-1.0>
    },
    "evidence": {
      "one_action_evidence": "<evidence>",
      "one_avoidance_or_friction_evidence": "<evidence>",
      "one_next_correction": "<correction>"
    },
    "verdict_label": "<label>",
    "verdict_sentence": "<sentence>",
    "save": true
  }'
```

Valid verdict labels: `aligned_progress`, `noisy_progress`, `avoidance_disguised_as_work`, `recovery_week`, `unstable_but_useful`, `blocked_by_environment`

### 5. Update Evidence and Counters

1. Fill evidence template for the week
2. Update validation counters
3. Update governance docs
4. Commit and push

## Count Rules

- Only records after 2026-05-28 count
- P10-M2, P10-M3, P11 smoke, P11-PILOT-1 do not count
- Provider output does not count
- Synthetic evidence does not count

## Pattern Review Timing

- Optional before Week 4
- Required before closeout
- Should evaluate valid post-start evidence
- If insufficient_data, record as supporting status only

## Friction Classification

| Severity | Definition | Allowed? | Requirements |
|----------|------------|----------|--------------|
| blocker | Cannot complete weekly note/review/score | Yes with approval | GPT/Charlie approval, logged |
| high | Risks corrupting validation evidence | Yes with approval | GPT/Charlie approval, logged |
| medium | Confusing but workaround exists | Defer until after P6 closeout | Unless materially affects evidence quality |
| low | Cosmetic or preference | Defer until after P6 closeout | No |

## Local Backup Routine

### Dry-run

```bash
alters-lab backup --dry-run --json
```

### Real backup

```bash
alters-lab backup --output ~/alters-lab-backups/week<N>-post-validation-backup.tar.gz
```

- Keep archive local
- Do not commit backup archive

## Non-Countable Evidence (Reminder)

- P10-M2 does not count
- P10-M3 does not count
- P11 smoke does not count
- P11-PILOT-1 does not count
- Provider output does not count
- Synthetic data does not count

## Hard Boundaries

- No alters/current/** changes
- No alters/calibration/rubric.yaml changes
- No runtime records committed
- No raw weekly note/review content committed
- No provider secrets committed
- No real provider calls
- No provider output committed
- No P6 validated claim
- No P6 sealed claim
