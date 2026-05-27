# P6 Skip Decision Record

## Decision

**P6_SKIPPED_VALIDATION** — Human decision to skip the 4-week real-use validation phase for Phase 6 (Personal Long-Term Use Hardening).

## Date

2026-05-27

## Context

Phase 6 code-complete status was accepted and merged to main at `cdf4d4e6bf20c3ed160c429c1520dd1ec74917e1`. All P6-M1 through P6-M11 backend routes, services, and schemas are implemented. 840 backend tests passing.

P6 originally required a 4-week real-use validation window including:
- 4 weekly reviews
- 4 calibration records
- 1 pattern review
- A real 4-week evidence window

This validation was blocked by the real-use window requirement and was never initiated.

## Rationale

The human decision to skip P6 validation was made to unblock project progression to Phase 8 (Real Provider Integration & End-to-End Validation). The code is functionally complete but has not been validated through actual real-use.

## Consequences

- P6 status: `CODE_COMPLETE / P6_SKIPPED_VALIDATION`
- P6 is **not sealed** and **not behavior validated**
- P6 code is accepted as-is — functional but unvalidated through real use
- No regression risk to P7 (local app distribution) or P8 (provider integration)
- Future real-use validation could still be performed manually if desired

## Status

| Field | Value |
|-------|-------|
| Decision | SKIP |
| Authority | Human (project owner) |
| P6 Code Status | CODE_COMPLETE |
| P6 Validation Status | SKIPPED |
| P6 Seal Status | NOT_SEALED |
| Reversibility | Validation can still be performed manually at any time |

## Related Artifacts

- `docs/harness/P8_000_REAL_PROVIDER_AND_E2E_PLAN.md` — P8 plan referencing this decision
- `docs/harness/PROJECT_BOARD.md` — Updated with P6_SKIPPED_VALIDATION status
