# P8 Taskbook

## Phase 8 — Real Provider & Product Readiness

### P8-000: Real Provider & Product Readiness Boundary Plan

**Status**: done
**Goal**: Define the next phase boundary before implementing real provider behavior.
**Depends on**: P7-R1 complete
**Notes**: Created P8 plan, taskbook, provider safety boundary, and E2E validation plan. Defined provider threat model, safety policy, milestone table, and hard boundaries.

### P8-M1: Provider Adapter Contract Hardening

**Status**: done
**Goal**: Define a clean provider adapter boundary with disabled/mock/openai-compatible-http modes, timeout behavior, retry behavior, redaction, no persistence by default, no active YAML write, no score generation.
**Depends on**: P8-000 reviewed and approved
**Notes**: Done. Provider adapter schema/service/API with Literal[False] safety fields, disabled/mock/openai-compatible-http modes, request.mode override protections.

### P8-M2: Real Provider Dry-Run / Connectivity Check

**Status**: done
**Goal**: Allow user-configured provider to perform an explicit safe connectivity check. User must explicitly enable live_check. No prompts containing personal records by default. No provider output persisted. No secrets returned. All network attempts audited locally with redacted metadata.
**Depends on**: P8-M1
**Notes**: Done. Connectivity check with /models endpoint, exact confirmation gating, fake http_client in tests.

### P8-M3: Provider-Backed Dialogue Preview

**Status**: done
**Goal**: Allow optional provider-backed response generation for Alter Dialogue only. save_session=false default, no active YAML writes, no calibration writes, no reality score writes, output displayed as preview, user can copy manually, provider output must be labeled unverified.
**Depends on**: P8-M2
**Notes**: Done. Dialogue preview schemas, service, and API routes. Uses /chat/completions endpoint, injectable http_client, prompt/system_prompt capping, max_tokens/temperature controls.

### P8-M4: Weekly Review Assistant Mode

**Status**: done
**Goal**: Use provider only as an optional assistant inside Weekly Review UI. User explicitly clicks "Generate suggestion", output cannot submit the review automatically, user must manually edit/confirm, action alignment scores remain user-submitted, no automatic scoring.
**Depends on**: P8-M3
**Notes**: Done. Weekly review assistant schemas/service/API/frontend. Reuses provider_dialogue_preview for actual provider calls. Advisory-only suggestions, copy-only UI.

### P8-M5: E2E Product Validation

**Status**: done
**Goal**: Run local app end-to-end: install package or package-context smoke, open frontend, configure mock provider, run weekly review flow with synthetic smoke data, verify packaged runtime writes to user data dir, verify backup excludes secrets, verify P6 still not validated/sealed.
**Depends on**: P8-M4
**Notes**: Done. E2E smoke script with package-context isolated HOME. 12 smoke sections (A-M). Evidence redacted (no provider output content). 22 smoke tests.

### P8-M6: Provider Safety Audit

**Status**: done
**Goal**: Explicit checks: no API key in committed evidence, no provider output in committed evidence, no provider service imports mutation paths, LIVE_CONFIRMATION constants present, Literal[False] safety fields in provider schemas.
**Depends on**: P8-M5
**Notes**: Done. 7 audit sections all PASS: grep scan (0 disallowed), route audit (5/5 found), live constants (3/3 found), schema safety (5 files, 0 issues), evidence contract (no provider output, p6 false flags), secret policy (no direct _fallback_get), mutation boundary (0 violations). 35 tests.

### P8-M7: P8 Closeout

**Status**: done
**Goal**: Seal P8 only if: real provider boundary is implemented safely, E2E validation passes, no secrets leaked, P6 remains separate, P7 local app remains installable.
**Depends on**: P8-M6
**Notes**: Done. P8 sealed as REAL_PROVIDER_READY_LOCAL_APP. All verification checks pass: 1215 backend tests, frontend build, route inventory (157 routes), active YAML/rubric diff clean, no runtime records committed, no secrets committed, no provider output in evidence.

## P8 Sealed Baseline

P8 Final Gate: **REAL_PROVIDER_READY_LOCAL_APP**
- Backend tests: 1215 passed
- Frontend build: PASS
- Route inventory: PASS (157 routes)
- Provider safety audit: PASS (7 sections)
- P8 E2E smoke: PASS (12 sections)
- Active YAML diff: clean
- Rubric diff: clean
- P6: CODE_COMPLETE / NOT_VALIDATED / NOT_SEALED
- P7: sealed as LOCAL_APP_RELEASE_CANDIDATE
