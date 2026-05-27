# P8-M1 Provider Adapter Contract

## Summary

Hardened provider adapter contract layer that supports disabled, mock, and openai-compatible-http modes without making real provider calls.

## Architecture

```
ProviderAdapterRequest
    → validate_provider_request() [blocks live_check, persist_output]
    → run_provider_adapter()
        → disabled: status=skipped, no output
        → mock: status=ok, deterministic preview, no network
        → openai-compatible-http: dry-run only, no network
    → build_provider_audit_event() [metadata only]
    → ProviderAdapterResponse [explicit safety flags]
```

## Files

| File | Purpose |
|------|---------|
| `apps/api/src/alters_lab/schemas/provider_adapter.py` | Request/response/audit schemas |
| `apps/api/src/alters_lab/services/provider_adapter.py` | Adapter logic, audit events, validation |
| `apps/api/src/alters_lab/api/provider_adapter.py` | API routes (/health, /status, /preview) |
| `apps/api/tests/test_provider_adapter.py` | 17 service-level tests |
| `apps/api/tests/test_provider_adapter_api.py` | 9 API-level tests |

## API Routes

| Route | Method | Description |
|-------|--------|-------------|
| `/provider-adapter/health` | GET | Health check. real_network_calls_enabled=false. |
| `/provider-adapter/status` | GET | Provider mode, safety flags, supported modes. |
| `/provider-adapter/preview` | POST | Adapter preview by mode. live_check and persist_output blocked. |

## Safety Guarantees

| Guarantee | Enforcement |
|-----------|-------------|
| No real network calls | Tests verify network_call_made=false for all modes |
| live_check blocked | validate_provider_request returns "blocked" |
| persist_output blocked | validate_provider_request returns "blocked" |
| No active YAML writes | response.active_yaml_modified always false |
| No rubric writes | response.rubric_modified always false |
| No reality scores | response.reality_score_created always false |
| No action alignment | response.action_alignment_created always false |
| No secrets in response | No api_key fields, secrets_redacted=true |
| No secrets in audit | prompt_recorded=false, response_recorded=false, secret_recorded=false |
| P6 flags remain false | p6_behavior_validated=false, p6_sealed=false |

## Test Coverage (26 tests)

1. disabled mode returns skipped, network_call_made=false
2. mock mode returns deterministic preview, network_call_made=false
3. openai-compatible-http dry-run makes no network call
4. live_check=true is blocked, no network call
5. persist_output=true is blocked
6. response never includes API key fields
7. audit event contains no raw prompt/response/secret
8. audit event redacted=true
9. no active YAML/rubric writes
10. no reality score/action alignment creation
11. p6 false flags remain false
12. /health returns real_network_calls_enabled=false
13. /status exposes safety flags
14. /preview works for mock
15. /preview blocks live_check
16. existing provider-config tests still pass
17. validate_provider_request blocks live_check
18. validate_provider_request blocks persist_output
19. validate_provider_request allows normal
20. redact_provider_error masks details
