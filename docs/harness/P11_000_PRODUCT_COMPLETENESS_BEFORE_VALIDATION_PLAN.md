# P11-000: Product Completeness Before Validation Plan

## Purpose

Audit and complete missing app functionality before P6 validation can begin.

Charlie decided: P6 validation is BLOCKED because the app is not yet functionally complete enough for normal daily use. P11 fills that gap.

## Current State

- P10-M5 done: BLOCKED_BY_NEW_FRICTION (product incompleteness)
- P6: CODE_COMPLETE / NOT_VALIDATED / NOT_SEALED
- P10-M6/M7: blocked
- App can execute a first real weekly note/review flow, but overall functionality is incomplete

## Proposed Milestones

| ID | Title | Purpose |
|----|-------|---------|
| P11-000 | Product Completeness Before Validation Plan | This plan |
| P11-M1 | Current app capability inventory | Catalog all existing pages, APIs, data flows, user tasks |
| P11-M2 | Missing core workflow map | Identify what's incomplete or half-built |
| P11-M3 | UX gaps and normal-use blockers | Find friction that prevents daily use |
| P11-M4 | Data model/API/frontend gap closure plan | Plan what needs to be built/fixed |
| P11-M5 | Product completion implementation batch 1 | First round of fixes |
| P11-M6 | Product completion implementation batch 2 | Second round of fixes |
| P11-M7 | Product completeness smoke and closeout | Verify app is ready for P6 validation |

## Excluded Scope

- No P6 validation start
- No P6 seal
- No raw personal records committed
- No provider output persistence by default
- No active YAML/rubric mutation
- No SaaS/cloud unless separately approved

## Hard Boundaries

- No changes to `alters/current/**`
- No changes to `alters/calibration/rubric.yaml`
- No runtime records committed
- No personal weekly note/review content committed
- No provider secrets committed
- No real provider calls
- No P6 validation claim
- No P6 seal
- No P10-M6 start

## Exit Gate

P11 is complete when:
- App capability inventory is documented
- Missing workflows are mapped
- UX blockers are identified
- Gap closure plan is approved
- Implementation batches are done
- Smoke test passes
- App is ready for P6 validation start decision (revisit P10-M5)
