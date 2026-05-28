# P12-000: UI Override Plan and Validation Pause

**Date:** 2026-05-28
**Decision:** Owner override — proceed with UI improvements during validation window

## Owner Decision

Charlie (owner) explicitly requested UI improvements now, including:
1. Tailwind CSS visual baseline
2. GSAP animation layer
3. Chinese/English i18n toggle
4. Loading and error-state system
5. New-user guided path

## P6 State Change

| Field | Before | After |
|-------|--------|-------|
| P6 state | CODE_COMPLETE / VALIDATION_IN_PROGRESS / NOT_SEALED | CODE_COMPLETE / VALIDATION_PAUSED_FOR_PRODUCT_CHANGE / NOT_SEALED |
| Week 1 evidence | Counted toward closeout | Preserved but not counted by default |
| Validation window | Active | Paused |

## P12 Milestone Plan

| ID | Title | Status |
|----|-------|--------|
| P12-000 | Owner override plan and validation pause | **done** |
| P12-M1 | Tailwind visual baseline | **ready_with_approval** |
| P12-M2 | Loading and error-state system | **blocked** |
| P12-M3 | i18n zh/en toggle | **blocked** |
| P12-M4 | New-user guided path | **blocked** |
| P12-M5 | GSAP motion layer | **blocked** |
| P12-M6 | Product smoke and real-use pilot | **blocked** |
| P12-M7 | P6 validation restart decision | **blocked** |

## Scope Boundaries

### Allowed After Planning Approval

- Frontend UI code changes
- Tailwind config
- Package dependency changes (gsap, tailwind, i18n libs)
- i18n frontend dictionary
- GSAP frontend motion layer
- Docs/governance updates

### Not Allowed

- Backend behavior changes (unless separately approved)
- Active YAML/rubric mutation
- Provider behavior changes
- Real provider calls
- Runtime records committed
- Raw personal content committed
- P6 validated/sealed claim

## Acceptance Criteria

- App remains packaged-app usable
- Weekly note → weekly review → action alignment still works
- Provider disabled/mock behavior preserved
- No real provider call by default
- Frontend build passes
- Backend tests pass
- Package build passes
- Product smoke passes
- UI/i18n/animation do not hide failed writes
- Reduced motion respected or animations can be disabled

## Week 1 Evidence Treatment

Week 1 evidence (commit 14ee9d5) remains preserved in the repo but is not counted toward P6 final closeout by default. After UI stabilization, validation start gate will be reopened.

## Post-P12 Plan

After P12-M6 (product smoke and real-use pilot), a decision will be made on P12-M7:
- If UI changes are stable and app is usable → reopen P6 validation
- If UI changes introduced issues → fix before reopening validation
