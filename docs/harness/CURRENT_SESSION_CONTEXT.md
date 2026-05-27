# Current Session Context

Last updated: 2026-05-27

## Project State

- P7 sealed as `LOCAL_APP_RELEASE_CANDIDATE`
- P7-R1 (frontend Weekly Review usability) complete
- P6: `CODE_COMPLETE / NOT_VALIDATED / NOT_SEALED`
- P8-000: done (boundary plan created)
- P8-M1: done (provider adapter contract hardened)
- P8-M2: done (connectivity check with /models endpoint, exact confirmation gating)
- P8-M3: done (provider-backed dialogue preview with /chat/completions, injectable http_client)
- P8-M4: ready_with_approval (Weekly Review assistant mode)
- P8-M5 through P8-M7: blocked
- No active phase in progress

## What Was Just Completed

P8-M3: Provider-Backed Dialogue Preview.
- Created provider dialogue preview schemas, service, and API routes
- Uses /chat/completions endpoint, injectable http_client, prompt/system_prompt capping
- persist_output and save_session blocked. live_generation requires exact confirmation.
- 36 new tests, 1117 total backend tests passing
- P8-M4 ready_with_approval

## Next Decision

P8-M4 (Weekly Review Assistant Mode) is ready_with_approval.
Requires explicit human/GPT approval before starting.

## Verification Commands

```bash
# Backend tests
PYTHONPATH=apps/api/src python3 -m pytest apps/api/tests/ -q

# Frontend build
cd apps/web && npm run build

# Type check
cd apps/web && npx tsc --noEmit

# Git status
git status
```

## Key Boundaries

- No `alters/current/**` changes without approval
- No runtime records committed
- No P6 validation claims
- No P8 restart without approval
- No live provider calls without explicit configuration
