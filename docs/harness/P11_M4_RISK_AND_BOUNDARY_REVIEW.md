# P11-M4: Risk and Boundary Review

## Hard Boundaries (Must Preserve)

| Boundary | Status | Notes |
|----------|--------|-------|
| No P6 validation start | PRESERVED | M5/M6 build UI only. No validation trigger. |
| No P6 seal | PRESERVED | P6 remains CODE_COMPLETE / NOT_VALIDATED / NOT_SEALED |
| No provider output persistence by default | PRESERVED | No provider calls in M5/M6 scope |
| No active YAML/rubric mutation | PRESERVED | Frontend-only changes, no backend writes to active YAML |
| No real provider calls | PRESERVED | All features work with mock/disabled provider |
| No secrets committed | PRESERVED | No secret handling in frontend changes |
| No runtime records committed | PRESERVED | No record creation in M5/M6 scope (UI reads existing data) |
| No frontend for historical Phase 3-6 internal routes | PRESERVED | M5/M6 focus on user-facing P6 workflows only |
| No SaaS/cloud/mobile scope | PRESERVED | Local app only |

## Risk Assessment

### P11-M5 Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| CalibrationHistory detail panel shows stale data | Low | Low | API returns live data on each load |
| Trend indicator misleads with <2 scores | Low | Low | Show "first score" indicator for single score |
| P6Progress false flags break | Low | High | Preserve existing P6 flag logic, add user-facing labels on top |
| Verdict explanation copy is inaccurate | Low | Low | Copy matches backend enum values exactly |
| Dynamic alter loading fails silently | Low | Low | Fallback to empty list if API fails |

### P11-M6 Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Pattern review build takes too long | Low | Low | Existing backend is synchronous, timeout at 30s |
| Behavior validation evaluates incorrectly | Low | Medium | Backend validates persisted evidence, not request booleans |
| Data management delete accidentally removes data | Low | High | Confirmation dialog required, no bulk delete |
| Export includes sensitive content | Low | Medium | Export uses existing API which excludes secrets by default |
| New pages break navigation | Low | Low | Frontend build must pass before commit |

## No-Go Conditions

P11-M5 or P11-M6 must NOT proceed if:

1. Any active YAML file is modified
2. Any provider is called without explicit configuration
3. Any secret is committed
4. Any P6 validation claim is made
5. Any runtime record is committed
6. Backend tests fail
7. Frontend build fails

## Boundary Confirmation Checklist

- [ ] No changes to `alters/current/**`
- [ ] No changes to `alters/calibration/rubric.yaml`
- [ ] No runtime records committed
- [ ] No personal weekly note/review content committed
- [ ] No provider secrets committed
- [ ] No real provider calls
- [ ] No code changes in M4 (planning only)
- [ ] No frontend implementation in M4 (planning only)
- [ ] No backend implementation in M4 (planning only)
- [ ] No P6 validation claim
- [ ] No P6 seal
- [ ] No P11-M5 implementation in M4
