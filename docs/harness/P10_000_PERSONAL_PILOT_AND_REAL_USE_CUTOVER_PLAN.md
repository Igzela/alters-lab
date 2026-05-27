# P10-000: Personal Pilot & Real-Use Cutover Boundary Plan

## Summary

Defines the next phase for moving Alters Lab from a sealed local product into Charlie's actual daily/weekly use, without prematurely claiming P6 validation.

## Current Accepted State

- P7 sealed as `LOCAL_APP_RELEASE_CANDIDATE`
- P8 sealed as `REAL_PROVIDER_READY_LOCAL_APP`
- P9 sealed as Release Hygiene & Install Readiness complete
- P6: `CODE_COMPLETE / NOT_VALIDATED / NOT_SEALED`
- P6 real 4-week validation has not started

## P10 Purpose

- Operational cutover into real use
- Evidence discipline
- Product friction discovery
- Bridge toward possible P6 validation

P10 is not a feature expansion phase. P10 is an operational cutover / dogfooding / real-use readiness phase.

## Milestone Table

| ID | Title | Status | Depends on |
|----|-------|--------|------------|
| P10-000 | Personal Pilot & Real-Use Cutover Boundary Plan | done | P9-M7 |
| P10-M1 | Local installation cutover checklist | ready_with_approval | P10-000 |
| P10-M2 | First real weekly note ingest | blocked | P10-M1 |
| P10-M3 | First real weekly review session | blocked | P10-M2 |
| P10-M4 | Real-use friction log and fix triage | blocked | P10-M3 |
| P10-M5 | P6 validation start decision gate | blocked | P10-M4 |
| P10-M6 | Week 1 validation package (only if Charlie explicitly starts P6 validation) | blocked | P10-M5 |
| P10-M7 | Pilot closeout / next phase decision | blocked | P10-M6 |

## P10 Excluded Scope

- No major new product features
- No SaaS/cloud deployment
- No mobile/Windows/macOS packaging
- No automatic provider output persistence
- No automatic P6 validation
- No P6 seal
- No active YAML/rubric mutation from provider output
- No background provider calls

## Hard Boundaries

- Do not modify `alters/current/**`
- Do not modify `alters/calibration/rubric.yaml`
- Do not commit raw runtime records
- Do not commit personal weekly notes
- Do not commit provider secrets
- Do not run real provider calls
- Do not claim P6 validation
- Do not seal P6
- Do not start P10-M1 implementation

## P6 Validation Bridge

P6 validation can begin only after an explicit human/GPT decision and must require:

- Real weekly note record
- Real weekly review
- Calibration record
- Action alignment score
- Weekly review completion
- No synthetic smoke evidence
- No provider-output-as-evidence
- Clear start date

## Real-Use Evidence Policy

- Raw personal records stay local
- Repo may store redacted summaries only
- No secrets
- No raw weekly notes
- No provider prompts/responses
- Evidence summaries must state whether real or synthetic

## Product Friction Policy

During pilot, product fixes are allowed only if:

- Discovered during real use
- Small and scoped
- Do not alter P6 validation criteria
- Documented as friction fix
- Do not rewrite history/evidence

## Risks

| Risk | Mitigation |
|------|------------|
| Confusing P10 pilot with P6 validation | Clear separation in all docs |
| Using synthetic records as real evidence | Evidence policy enforced |
| Overbuilding instead of using | P10 excluded scope blocks feature work |
| Provider suggestions influencing validation improperly | P6 validation criteria independent of provider |
| Committing personal records | Hard boundary: no raw records committed |
| Install/runtime drift from packaged app | P10-M1 cutover checklist |
| Ignoring friction because docs say it should work | Friction log captures real issues |

## Success Standard

P10-000 succeeds when the repo clearly tells a new session:

- Product is ready for personal pilot
- P6 is not validated
- Next step is installation cutover, not feature expansion
- P6 validation requires explicit start decision
