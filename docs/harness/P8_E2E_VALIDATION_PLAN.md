# P8 E2E Validation Plan

## Test Levels

### Level 1: Mock-Only Local Smoke

**Provider mode**: mock
**What to test**:
- Start local server
- Load frontend
- Navigate all pages
- Ingest synthetic weekly note
- Complete weekly review flow
- Submit action alignment score
- Verify P6 flags remain false
- Stop server

**P6 claim**: None

### Level 2: Dry-Run Real Provider Config

**Provider mode**: openai-compatible-http
**What to test**:
- Configure real provider endpoint (no real key)
- Run connectivity check (expected: connection refused or auth error)
- Verify redacted status response
- Verify no secrets in response
- Verify audit event logged

**P6 claim**: None

### Level 3: Optional Live Provider Smoke

**Provider mode**: openai-compatible-http
**What to test**:
- Human provides a test API key
- Configure provider with test key
- Run connectivity check (expected: success)
- Run one dialogue preview with synthetic prompt
- Verify output labeled unverified
- Verify no output persisted automatically
- Verify no active YAML changes
- Verify no secrets in logs
- Remove test key after smoke

**P6 claim**: None
**Requirement**: Human must provide test key explicitly

### Level 4: Package-Context Smoke

**Provider mode**: mock
**What to test**:
- Build .deb package
- Extract to isolated HOME
- Start packaged launcher
- Load FastAPI-served frontend
- Run full weekly review flow with mock provider
- Run backup dry-run
- Verify backup excludes secrets
- Verify P6 flags remain false
- Stop server

**P6 claim**: None

### Level 5: Frontend Flow Smoke

**Provider mode**: mock
**What to test**:
- Load frontend
- Navigate to each page: Status, Weekly Review, Dialogue, Reality Score, History, Rubric Delta, Checkpoint Plan, Provider
- Verify no JavaScript errors
- Verify no API errors
- Verify P6 progress panel shows false flags
- Verify Provider page shows redacted config

**P6 claim**: None

## Pass Criteria

P8 E2E validation passes when:
- All 5 levels pass
- No secrets leaked in any level
- No active YAML modified in any level
- No rubric modified in any level
- P6 remains NOT_VALIDATED / NOT_SEALED in all levels
- No runtime records committed

## Excluded

- No P6 behavior validation claim
- No P6 seal claim
- No automatic scoring validation
- No long-running provider stress test
- No multi-user concurrency test
