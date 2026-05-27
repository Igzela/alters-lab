# P10-M2: First Real Weekly Note Ingest

## Goal

Guide Charlie's first real weekly note ingest using the packaged local app, without committing raw personal content.

**This milestone cannot be completed with synthetic data.** Charlie must perform the actual operation.

## Preconditions

- P10-M1 cutover completed (packaged app installed)
- App launched from packaged command, not repo/dev mode
- Provider disabled or mock only
- No real provider call required
- P6 validation not started

## Local Commands

```bash
which alters-lab
alters-lab doctor --json
alters-lab status
alters-lab start
alters-lab open
```

## In-App Steps

1. Open http://127.0.0.1:18790
2. Go to **Weekly Review**
3. Paste one real weekly note from your actual Obsidian/week record
4. Ingest/import the note
5. Verify the app creates a weekly note/product record locally
6. Do NOT submit a full weekly review yet (that's P10-M3)
7. Do NOT run provider live generation

## Evidence to Capture Locally

After completing the ingest, record locally:

- note_ingest_status
- weekly_note_record_created: true/false
- record_id or redacted record reference
- source_type: real_weekly_note
- synthetic: false
- provider_used: false or mock_only
- p6_validation_started: false
- p6_sealed: false

## Repo Evidence Policy

- Raw weekly note stays local
- No personal content in repo
- No provider prompts/responses
- No API keys
- No raw runtime records
- Redacted summary only

## Completion

P10-M2 is marked done only after Charlie confirms a real weekly note was ingested and provides a redacted evidence summary using `P10_M2_REAL_WEEKLY_NOTE_EVIDENCE_TEMPLATE.md`.
