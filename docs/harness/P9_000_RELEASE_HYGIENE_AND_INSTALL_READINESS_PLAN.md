# P9-000: Release Hygiene & Install Readiness Boundary Plan

## Summary

Defines the next phase for turning the sealed local app into a usable personal release: install docs, upgrade/remove verification, first-run guide, provider setup guide, troubleshooting, and release checklist.

## Current Accepted State

- P7 sealed as `LOCAL_APP_RELEASE_CANDIDATE`
- P8 sealed as `REAL_PROVIDER_READY_LOCAL_APP`
- P6: `CODE_COMPLETE / NOT_VALIDATED / NOT_SEALED`
- P9 starting as boundary plan only

## Milestone Table

| ID | Title | Status | Depends on |
|----|-------|--------|------------|
| P9-000 | Release Hygiene & Install Readiness Boundary Plan | done | P8-M7 |
| P9-M1 | User-facing install / launch / uninstall docs | ready_with_approval | P9-000 |
| P9-M2 | Disposable install/upgrade/remove verification | blocked | P9-M1 |
| P9-M3 | First-run onboarding guide | blocked | P9-M2 |
| P9-M4 | Provider setup and safety guide | blocked | P9-M2 |
| P9-M5 | Troubleshooting / doctor improvements | blocked | P9-M3 |
| P9-M6 | Release artifact checklist and version bump policy | blocked | P9-M5 |
| P9-M7 | P9 Closeout | blocked | P9-M6 |

## P9 Scope

Turn the sealed local app into a usable personal release:
- Install, launch, and uninstall documentation
- Disposable environment verification (install/upgrade/remove)
- First-run onboarding guide
- Provider setup and safety guide
- Troubleshooting and doctor improvements
- Release artifact checklist and version bump policy

## P9 Excluded Scope

- No SaaS/cloud deployment
- No multi-user support
- No mobile app
- No Windows/macOS packaging
- No automatic P6 validation
- No provider output persistence by default
- No active YAML/rubric mutation
- No background provider calls

## Release-Readiness Threat Model

| Threat | Impact | Mitigation |
|--------|--------|------------|
| Broken install | User cannot use the app | Disposable install smoke test |
| Broken upgrade | User loses data or config | Upgrade smoke test with data preservation check |
| Unsafe uninstall/delete | User data or secrets leaked | Uninstall smoke test, verify cleanup |
| Unclear provider setup | User confused about mock vs live | Provider setup guide with step-by-step instructions |
| User thinks P6 is validated | False confidence in behavior claims | Clear P6 state messaging in all docs |
| App works only from repo | Package is broken | Package-context smoke already validates this |
| Docs diverge from CLI behavior | User follows wrong instructions | Doc review against actual CLI behavior |
| Secrets in backup/support logs | Credential leak | Backup already excludes secrets, verify in smoke |

## Success Standard

P9 succeeds only when a fresh user/local machine can:
1. Install the package
2. Launch the app
3. Configure mock provider
4. Run a smoke test
5. Backup data
6. Uninstall/upgrade safely
7. Understand P6/P8 boundaries

## Required Future Evidence

- Package install smoke in disposable environment
- Uninstall/remove smoke
- Upgrade smoke
- User docs review
- Doctor output review
- Provider setup guide review
- Release checklist evidence

## Hard Boundaries

- Do not modify `alters/current/**`
- Do not modify `alters/calibration/rubric.yaml`
- Do not commit runtime records
- Do not commit provider secrets
- Do not run real provider calls
- Do not claim P6 validation
- Do not seal P6
- Do not start implementation milestones after P9-000 without approval
