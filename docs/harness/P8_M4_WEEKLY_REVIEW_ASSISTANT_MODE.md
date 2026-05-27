# P8-M4 Weekly Review Assistant Mode

## Summary

Optional provider assistance inside the Weekly Review flow. Provider suggests; user decides and submits. Advisory-only, unverified, non-persistent.

## Architecture

```
WeeklyReviewAssistantRequest
    → run_weekly_review_assistant()
        → disabled: status=skipped, no network
        → mock: status=ok, no network, deterministic unverified suggestion
        → openai-compatible-http:
            → not configured: status=blocked
            → dry_run: status=ok, no network
            → live_generation=false: status=blocked
            → live_generation without confirmation: status=blocked
            → live_generation with wrong confirmation: status=blocked
            → live_generation with exact confirmation:
                → delegates to provider_dialogue_preview
                    → builds prompt from requested_help + context
                    → uses SYSTEM_PROMPT for unverified suggestion
                    → returns suggestion to user
    → _build_audit_event() [metadata only]
    → WeeklyReviewAssistantResponse [Literal-locked safety fields]
```

## Files

| File | Purpose |
|------|---------|
| `apps/api/src/alters_lab/schemas/weekly_review_assistant.py` | Request/response/audit schemas with Literal-locked safety fields |
| `apps/api/src/alters_lab/services/weekly_review_assistant.py` | Assistant logic, prompt builder, delegates to provider_dialogue_preview |
| `apps/api/src/alters_lab/api/weekly_review_assistant.py` | API routes (/health, /status, /suggest) |
| `apps/web/src/pages/WeeklyReview.tsx` | Frontend Assistant Suggestion section in Step 4 |
| `apps/web/src/api.ts` | API functions for weekly review assistant |
| `apps/api/tests/test_weekly_review_assistant.py` | 25 service-level tests |
| `apps/api/tests/test_weekly_review_assistant_api.py` | 8 API-level tests |

## API Routes

| Route | Method | Description |
|-------|--------|-------------|
| `/weekly-review-assistant/health` | GET | Health check. live_generation_supported=true, requires_confirmation=true. |
| `/weekly-review-assistant/status` | GET | Provider mode, configured, safety flags, P6 false flags. |
| `/weekly-review-assistant/suggest` | POST | Generate suggestion. dry_run default, live requires exact confirmation. |

## Safety Guarantees

| Guarantee | Enforcement |
|-----------|-------------|
| No real network in dry_run | Tests verify network_call_made=false |
| live_generation requires exact confirmation | confirmation="run-live-weekly-review-assistant" |
| Output is advisory only | suggestion_label=Literal["unverified_provider_suggestion"] |
| Output never persisted | suggestion_persisted=Literal[False] |
| Review never auto-completed | weekly_review_completed=Literal[False] |
| No action alignment scores | action_alignment_created=Literal[False] |
| No reality scores | reality_score_created=Literal[False] |
| No active YAML writes | active_yaml_modified=Literal[False] |
| No rubric writes | rubric_modified=Literal[False] |
| P6 flags remain false | p6_behavior_validated=Literal[False], p6_sealed=Literal[False] |
| No API key in response | Tests verify no key in response |
| Prompt not persisted | prompt_persisted=Literal[False] |
| Response not persisted | response_content_persisted=Literal[False] |
| save_suggestion blocked | Tests verify save_suggestion returns blocked |

## Frontend Behavior

- Assistant Suggestion section appears in Step 4 (Complete Review)
- requested_help select with 6 options
- "Generate dry-run suggestion" button (always available)
- "Generate live provider suggestion" button (only when provider is openai-compatible-http and configured)
- Live generation requires exact confirmation input: "run-live-weekly-review-assistant"
- Output displayed in labeled box: "Unverified provider suggestion"
- Copy buttons: review_note, dialogue_summary, primary_next_correction
- Copy buttons only fill local form fields, never auto-submit

## Requested Help Types

| Type | Instruction |
|------|-------------|
| summarize_facts | Summarize the key observable facts from this weekly note |
| identify_friction | Identify friction or avoidance points in this weekly note |
| draft_primary_correction | Draft a primary next correction based on this weekly review context |
| suggest_supporting_actions | Suggest 1-2 supporting actions for next week |
| challenge_avoidance | Gently challenge any avoidance patterns you see in this note |
| general_review_suggestion | Provide a general review suggestion based on the available context |
