# P9 Taskbook

## Phase 9 — Release Hygiene & Install Readiness

### P9-000: Release Hygiene & Install Readiness Boundary Plan

**Status**: done
**Goal**: Define the next phase for turning the sealed local app into a usable personal release.
**Depends on**: P8-M7 complete
**Notes**: Created P9 plan, taskbook, release readiness boundary, and user-facing docs plan. Defined threat model, success standard, milestone table, and hard boundaries.

### P9-M1: User-facing install / launch / uninstall docs

**Status**: ready_with_approval
**Goal**: Create clear documentation for installing, launching, and uninstalling the app from a .deb package. Cover first launch, CLI commands, data directory locations, and clean uninstall.
**Depends on**: P9-000 reviewed and approved
**Notes**: Not started. Requires explicit approval.

### P9-M2: Disposable install/upgrade/remove verification

**Status**: blocked
**Goal**: Verify that install, upgrade, and remove work correctly in a disposable environment (tmpdir or container). Verify data preservation on upgrade, clean removal on uninstall, no secret leakage.
**Depends on**: P9-M1
**Notes**: Blocked.

### P9-M3: First-run onboarding guide

**Status**: blocked
**Goal**: Create a first-run guide that helps new users understand what the app does, how to configure it, and what the P6/P8 boundaries mean. Could be in-app or standalone docs.
**Depends on**: P9-M2
**Notes**: Blocked.

### P9-M4: Provider setup and safety guide

**Status**: blocked
**Goal**: Create a guide for setting up a provider (mock or live), explaining the safety model, confirmation gating, and what the provider can/cannot do.
**Depends on**: P9-M2
**Notes**: Blocked.

### P9-M5: Troubleshooting / doctor improvements

**Status**: blocked
**Goal**: Improve the `alters-lab doctor` command to check for common issues: missing config, broken package, provider misconfiguration, data directory permissions. Add troubleshooting docs.
**Depends on**: P9-M3
**Notes**: Blocked.

### P9-M6: Release artifact checklist and version bump policy

**Status**: blocked
**Goal**: Create a release checklist (tests pass, package builds, smoke passes, docs updated) and a version bump policy (when to bump major/minor/patch).
**Depends on**: P9-M5
**Notes**: Blocked.

### P9-M7: P9 Closeout

**Status**: blocked
**Goal**: Seal P9 only if: install/uninstall docs exist, disposable verification passes, onboarding guide exists, provider setup guide exists, doctor works, release checklist exists.
**Depends on**: P9-M6
**Notes**: Blocked.
