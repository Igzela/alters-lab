# P8-M3 Provider-Backed Dialogue Preview

## Summary

First content-generating provider feature. Output is preview-only, unverified, explicitly triggered, and non-persistent. Uses /chat/completions endpoint with injectable http_client for testing.

## Architecture

```
ProviderDialoguePreviewRequest
    → run_provider_dialogue_preview()
        → disabled: status=skipped, no network
        → mock: status=ok, no network, unverified preview text
        → openai-compatible-http:
            → not configured: status=blocked
            → dry_run: status=ok, no network
            → live_generation=false: status=blocked
            → persist_output=true: status=blocked
            → save_session=true: status=blocked
            → live_generation without confirmation: status=blocked
            → live_generation with wrong confirmation: status=blocked
            → live_generation with exact confirmation: /chat/completions POST via http_client
                → 2xx: extracts choices[0].message.content
                → 401/403: error=auth_failed
                → timeout: error=connection_error
                → invalid JSON: error=invalid_response
    → build_provider_dialogue_preview_audit_event() [metadata only]
    → ProviderDialoguePreviewResponse [Literal-locked safety fields]
```

## Files

| File | Purpose |
|------|---------|
| `apps/api/src/alters_lab/schemas/provider_dialogue_preview.py` | Request/response/audit schemas with Literal-locked safety fields |
| `apps/api/src/alters_lab/services/provider_dialogue_preview.py` | Dialogue preview logic, http_client injection, prompt/system_prompt capping |
| `apps/api/src/alters_lab/api/provider_dialogue_preview.py` | API routes (/health, /status, /generate) |
| `apps/api/tests/test_provider_dialogue_preview.py` | 29 service-level tests |
| `apps/api/tests/test_provider_dialogue_preview_api.py` | 7 API-level tests |

## API Routes

| Route | Method | Description |
|-------|--------|-------------|
| `/provider-dialogue-preview/health` | GET | Health check. live_generation_supported=true, requires_confirmation=true. |
| `/provider-dialogue-preview/status` | GET | Provider mode, configured, safety flags. |
| `/provider-dialogue-preview/generate` | POST | Generate preview. dry_run default, live requires exact confirmation. |

## Safety Guarantees

| Guarantee | Enforcement |
|-----------|-------------|
| No real network in dry_run | Tests verify network_call_made=false |
| live_generation requires exact confirmation | confirmation="run-live-provider-dialogue-preview" |
| Output is preview-only | output_label=Literal["unverified_provider_preview"] |
| Output never persisted | output_persisted=Literal[False] |
| Session never saved | save_session=Literal[False] |
| Prompt never persisted | prompt_persisted=Literal[False] |
| Response content never persisted | response_content_persisted=Literal[False] |
| persist_output blocked | Tests verify persist_output returns blocked |
| save_session blocked | Tests verify save_session returns blocked |
| No API key in response | Tests verify no key in response |
| No active YAML writes | active_yaml_modified=Literal[False] |
| No rubric writes | rubric_modified=Literal[False] |
| No reality/action scores | reality_score_created=Literal[False], action_alignment_created=Literal[False] |
| P6 flags remain false | p6_behavior_validated=Literal[False], p6_sealed=Literal[False] |
| Prompt not recorded | prompt_recorded=Literal[False] |
| Response not recorded | response_recorded=Literal[False] |
| Secret not recorded | secret_recorded=Literal[False] |

## Input Caps

| Parameter | Min | Max | Default |
|-----------|-----|-----|---------|
| prompt | 1 char | 8000 chars | — |
| system_prompt | — | 4000 chars | "You are generating an unverified preview..." |
| temperature | 0.0 | 1.5 | 0.7 |
| max_tokens | 16 | 1200 | 512 |
