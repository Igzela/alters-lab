# P8 Taskbook

## Phase 8 — Real Provider & Product Readiness

### P8-000: Real Provider & Product Readiness Boundary Plan

**Status**: done
**Goal**: Define the next phase boundary before implementing real provider behavior.
**Depends on**: P7-R1 complete
**Notes**: Created P8 plan, taskbook, provider safety boundary, and E2E validation plan. Defined provider threat model, safety policy, milestone table, and hard boundaries. No code changes, no provider implementation, no real provider calls.

### P8-M1: Provider Adapter Contract Hardening

**Status**: ready_with_approval
**Goal**: Define a clean provider adapter boundary with disabled/mock/openai-compatible-http modes, timeout behavior, retry behavior, redaction, no persistence by default, no active YAML write, no score generation.
**Depends on**: P8-000 reviewed and approved
**Notes**: Not started. Requires explicit approval.

### P8-M2: Real Provider Dry-Run / Connectivity Check

**Status**: blocked
**Goal**: Allow user-configured provider to perform an explicit safe connectivity check. User must explicitly enable live_check. No prompts containing personal records by default. No provider output persisted. No secrets returned. All network attempts audited locally with redacted metadata.
**Depends on**: P8-M1
**Notes**: Blocked.

### P8-M3: Provider-Backed Dialogue Preview

**Status**: blocked
**Goal**: Allow optional provider-backed response generation for Alter Dialogue only. save_session=false default, no active YAML writes, no calibration writes, no reality score writes, output displayed as preview, user can copy manually, provider output must be labeled unverified.
**Depends on**: P8-M2
**Notes**: Blocked.

### P8-M4: Weekly Review Assistant Mode

**Status**: blocked
**Goal**: Use provider only as an optional assistant inside Weekly Review UI. User explicitly clicks "Generate suggestion", output cannot submit the review automatically, user must manually edit/confirm, action alignment scores remain user-submitted, no automatic scoring.
**Depends on**: P8-M3
**Notes**: Blocked.

### P8-M5: E2E Product Validation

**Status**: blocked
**Goal**: Run local app end-to-end: install package or package-context smoke, open frontend, configure mock provider, configure real provider only with explicit test secret if available, run weekly review flow with synthetic smoke data, verify packaged runtime writes to user data dir, verify backup still excludes secrets, verify P6 still not validated/sealed.
**Depends on**: P8-M4
**Notes**: Blocked.

### P8-M6: Provider Safety Audit

**Status**: blocked
**Goal**: Explicit checks: no API key returned in API response, no API key in logs, no API key in frontend state beyond password input lifecycle, no provider output writes active YAML, no provider output writes rubric, no provider output creates behavior validation, no raw runtime records committed.
**Depends on**: P8-M5
**Notes**: Blocked.

### P8-M7: P8 Closeout

**Status**: blocked
**Goal**: Seal P8 only if: real provider boundary is implemented safely, E2E validation passes, no secrets leaked, P6 remains separate, P7 local app remains installable.
**Depends on**: P8-M6
**Notes**: Blocked.
