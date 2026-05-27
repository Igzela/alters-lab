# P8-M2 Provider Connectivity Check

## Summary

Explicit real-provider connectivity checking for openai-compatible-http mode. Uses /models endpoint, exact confirmation gating, injectable http_client for tests.

## Architecture

```
ProviderConnectivityRequest
    → run_provider_connectivity_check()
        → disabled: status=skipped, no network
        → mock: status=ok, no network, provider_reachable=true
        → openai-compatible-http:
            → not configured: status=blocked
            → dry_run: status=ok, no network
            → live_check without confirmation: status=blocked
            → live_check with confirmation: /models GET via http_client
                → 2xx: reachable=true, auth_valid=true
                → 401/403: reachable=true, auth_valid=false
                → timeout: reachable=false
    → build_provider_connectivity_audit_event() [metadata only]
    → ProviderConnectivityResponse [Literal-locked safety fields]
```

## Files

| File | Purpose |
|------|---------|
| `apps/api/src/alters_lab/schemas/provider_connectivity.py` | Request/response/audit schemas with Literal-locked safety fields |
| `apps/api/src/alters_lab/services/provider_connectivity.py` | Connectivity logic, http_client injection, audit events |
| `apps/api/src/alters_lab/api/provider_connectivity.py` | API routes (/health, /status, /check) |
| `apps/api/tests/test_provider_connectivity.py` | 22 service-level tests |
| `apps/api/tests/test_provider_connectivity_api.py` | 8 API-level tests |

## API Routes

| Route | Method | Description |
|-------|--------|-------------|
| `/provider-connectivity/health` | GET | Health check. live_network_supported=true, requires_confirmation=true. |
| `/provider-connectivity/status` | GET | Provider mode, configured, key_configured, safety flags. |
| `/provider-connectivity/check` | POST | Connectivity check. dry_run default, live requires exact confirmation. |

## Safety Guarantees

| Guarantee | Enforcement |
|-----------|-------------|
| No real network in dry_run | Tests verify network_call_made=false |
| live_check requires exact confirmation | confirmation="run-live-provider-connectivity-check" |
| No user prompt content sent | /models endpoint used, no prompt field |
| No response body persisted | response_content_persisted=Literal[False] |
| No API key in response | Tests verify no key in response |
| No active YAML writes | active_yaml_modified=Literal[False] |
| No rubric writes | rubric_modified=Literal[False] |
| No reality/action scores | reality_score_created=Literal[False] |
| P6 flags remain false | p6_behavior_validated=Literal[False] |
| Prompt not recorded | prompt_recorded=Literal[False] |
| Response not recorded | response_recorded=Literal[False] |
| Secret not recorded | secret_recorded=Literal[False] |

## Test Coverage (30 tests)

1. disabled returns skipped, no network
2. mock returns ok, no network
3. openai unconfigured returns blocked, no network
4. dry_run returns no network
5. live_check without confirmation returns blocked
6. live_check wrong confirmation returns blocked
7. live_check exact confirmation uses injected client
8. 2xx maps reachable=true, auth_valid=true
9. 401 maps reachable=true, auth_valid=false
10. timeout maps reachable=false
11. response never includes API key
12. audit event contains no prompt/response/secret
13. no active YAML/rubric writes
14. p6 false flags remain false
15. prompt_content_sent=Literal[False]
16. response_content_persisted=Literal[False]
17-22. Contract hardening regression tests
23-30. API route tests
