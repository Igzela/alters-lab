# P8-000: Real Provider & Product Readiness Boundary Plan

## Status

P8-000 status: **PASS**

This plan defines the boundary for integrating real LLM provider capability into Alters Lab while preserving all safety guarantees established in P6 and P7.

## Current State

- P7 sealed as `LOCAL_APP_RELEASE_CANDIDATE`
- P7-R1 frontend Weekly Review usability layer complete
- P6: `CODE_COMPLETE / NOT_VALIDATED / NOT_SEALED`
- P8 starting now as boundary plan only
- No real provider calls in this plan
- No code implementation in this plan

## P8 Success Standard

P8 is successful only when real provider capability becomes safe, explicit, local, auditable, and non-mutating by default.

P8 is not successful merely because a provider call works.

## Milestone Table

| ID | Title | Status | Depends On |
|----|-------|--------|------------|
| P8-000 | Real Provider & Product Readiness Boundary Plan | **done** | P7-R1 |
| P8-M1 | Provider Adapter Contract Hardening | **ready_with_approval** | P8-000 |
| P8-M2 | Real Provider Dry-Run / Connectivity Check | **blocked** | P8-M1 |
| P8-M3 | Provider-Backed Dialogue Preview | **blocked** | P8-M2 |
| P8-M4 | Weekly Review Assistant Mode | **blocked** | P8-M3 |
| P8-M5 | E2E Product Validation | **blocked** | P8-M4 |
| P8-M6 | Provider Safety Audit | **blocked** | P8-M5 |
| P8-M7 | P8 Closeout | **blocked** | P8-M6 |

## Provider Threat Model

| Threat | Description | Mitigation |
|--------|-------------|------------|
| Secret leakage | API keys returned in responses, logged, or stored in frontend state | Redacted status/config responses, secret grep, no keys in logs/frontend |
| Prompt leakage | User personal records sent to provider without consent | Explicit opt-in, dry-run default, no personal records in connectivity check |
| Accidental persistence | Provider output written to active YAML, rubric, or reality scores | No provider output persistence by default, explicit user confirmation for any persisted semantic output |
| Automatic scoring | Provider output automatically creates action alignment or reality scores | All scores remain user-submitted, no automatic scoring |
| Hallucinated advice | Provider output mistaken as factual guidance | Provider output labeled unverified, user must manually edit/confirm |
| Active YAML mutation | Provider output writes to alters/current/** | Hard boundary: no provider output writes active YAML |
| Log sensitivity | Logs contain API keys or sensitive prompt/response content | Audit metadata only, not raw secrets or prompt content |
| Frontend secret storage | API keys stored in frontend state beyond input lifecycle | Keys only in password input, never in React state or localStorage |
| Network failure loops | Timeout/retry loops consuming resources or leaking data | Explicit timeout, no automatic retry, user-initiated only |

## Provider Safety Policy

1. **Explicit opt-in**: Real provider mode requires explicit user configuration. Default is disabled/mock.
2. **Dry-run default**: Connectivity check is dry-run by default. Live check requires explicit user action.
3. **Redacted status**: API responses never return provider keys. Status/config endpoints show `***` for secrets.
4. **No provider output persistence by default**: Provider responses are displayed as preview only. User must explicitly choose to save.
5. **No active YAML/rubric writes**: Provider output cannot write to `alters/current/**` or `alters/calibration/rubric.yaml`.
6. **User confirmation required**: Any persisted semantic output requires explicit user confirmation.
7. **Audit metadata only**: Network attempts are audited with redacted metadata (provider name, status code, latency). Raw secrets and prompt content are not logged.
8. **No background provider calls**: All provider interactions are user-initiated. No scheduled or background provider calls.

## E2E Validation Plan

| Level | Description | Provider Mode | P6 Claim |
|-------|-------------|---------------|----------|
| Mock-only local smoke | Full app flow with mock provider | mock | None |
| Dry-run real provider config | Configure real provider, run connectivity check | openai-compatible-http | None |
| Optional live provider smoke | Human provides test key, run one dialogue preview | openai-compatible-http | None |
| Package-context smoke | Install package, run full flow in isolated HOME | mock | None |
| Frontend flow smoke | Walk through all UI pages, verify no errors | mock | None |

No level claims P6 behavior validation.

## Required Future Artifacts

These files will be created during P8 implementation milestones, not in P8-000:

- `apps/api/src/alters_lab/services/provider_adapter.py` — Provider adapter service (P8-M1)
- `apps/api/src/alters_lab/schemas/provider_audit.py` — Provider audit schema (P8-M1)
- `apps/api/src/alters_lab/routers/provider_dialogue.py` — Provider dialogue preview route (P8-M3)
- `apps/web/src/pages/ProviderDialogue.tsx` — Frontend provider preview UI (P8-M3)
- `tools/p8_e2e_smoke.py` — E2E smoke script (P8-M5)
- `docs/harness/P8_CLOSEOUT_EVIDENCE.json` — P8 evidence (P8-M7)

## Hard Boundaries

- Do not modify `alters/current/**`
- Do not modify `alters/calibration/rubric.yaml`
- Do not commit runtime records
- Do not commit provider secrets
- Do not run real provider calls in P8-000
- Do not claim P6 behavior validation
- Do not seal P6
- Do not rewrite P7 closeout
- Do not start P8-M1 until P8-000 is reviewed

## Excluded Scope

- No SaaS/cloud deployment
- No multi-user support
- No database migration
- No mobile app
- No Windows/macOS packaging
- No automatic P6 behavior validation
- No automatic P6 seal
- No automatic rubric writes
- No automatic active YAML mutation
- No autonomous provider-driven long-term memory writes
- No background scheduled provider calls
