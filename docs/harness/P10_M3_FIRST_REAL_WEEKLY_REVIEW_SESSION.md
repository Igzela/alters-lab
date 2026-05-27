# P10-M3: First Real Weekly Review Session

## Preconditions

- P10-M2 done (first real weekly note ingested)
- One real weekly note record exists locally
- Packaged app installed and working
- Provider disabled or mock only
- No live provider generation
- P6 validation not started

## Local Commands

```bash
# Verify packaged app is installed and healthy
which alters-lab
alters-lab doctor --json
alters-lab status

# Start the app
alters-lab start

# Open in browser
alters-lab open
```

## In-App Steps

1. Open http://127.0.0.1:18790 in browser
2. Click "Weekly Review" in navigation
3. In Step 1 (Paste Weekly Note): load or select the real weekly note record from P10-M2
4. Click "Ingest note" to load the note
5. Proceed through Steps 2-5 of the weekly review wizard
6. Complete one real weekly review session manually
7. If assistant suggestion is used (Step 4), ensure:
   - Provider mode is mock only
   - No network call is made
   - Suggestion is advisory only — user must manually decide
8. Submit the review only after user edits/confirms content
9. Do NOT create P6 validation claim
10. Do NOT run live provider

## Evidence to Capture Locally

After completing the weekly review, fill in this evidence:

- weekly_review_completed: true/false
- weekly_review_record_created: true/false
- linked_weekly_note_reference: redacted
- review_record_reference: redacted
- source_type: real_weekly_review
- synthetic: false
- provider_used: false or mock_only
- assistant_suggestion_used: false/true
- if assistant used: provider_mode=mock, network_call_made=false
- p6_validation_started: false
- p6_sealed: false

## Repo Evidence Policy

- Raw review content stays local (not committed)
- No personal content in repo
- No provider prompts/responses
- No API keys
- No raw runtime records
- Redacted summary only in evidence file
