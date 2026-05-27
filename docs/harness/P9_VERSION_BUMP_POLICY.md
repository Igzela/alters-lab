# Version Bump Policy

Current version: `0.1.0`

## SemVer Rules

Alters Lab uses [Semantic Versioning](https://semver.org/): `MAJOR.MINOR.PATCH`

### PATCH (0.1.X)

Bug fixes, doc updates, test additions, governance-only changes, tooling improvements.

Bump when:
- Fixing a bug in existing behavior
- Updating documentation only
- Adding or improving tests
- Updating governance docs
- Improving CLI output or doctor checks

### MINOR (0.X.0)

New features, new CLI commands, new API endpoints, new frontend pages, provider mode additions.

Bump when:
- Adding a new CLI command
- Adding a new API endpoint or route group
- Adding a new frontend page
- Adding a new provider mode
- Adding a new backup/export feature
- Completing a project phase (P9, P10, etc.)

### MAJOR (X.0.0)

Breaking changes to CLI interface, API contracts, data format, or config schema.

Bump when:
- Changing CLI command names or flags in a non-backward-compatible way
- Changing API request/response schemas in a breaking way
- Changing config.yaml format requiring migration
- Changing data directory structure requiring migration
- Removing a supported provider mode

## Current History

| Version | Phase | Date | Notes |
|---------|-------|------|-------|
| 0.1.0 | P7-P9 | 2026-05 | Initial release. Local app, .deb package, CLI, provider modes, frontend MVP. |

## Where Version Lives

- `packaging/deb/control.template` — Debian package version
- `tools/build_deb.py` — Package filename version
- No hardcoded version in Python source (use importlib.metadata at runtime if needed)

## Phase Completion and Version Bumps

Phase completion does not automatically trigger a version bump. The decision is manual:

- If a phase adds user-facing features → bump MINOR
- If a phase is governance/docs/test-only → bump PATCH (or skip)
- If a phase breaks backward compatibility → bump MAJOR

P7 introduced the .deb package and CLI → 0.1.0 (initial release).
P8 added real provider support → remained 0.1.0 (new feature, but same install/upgrade path).
P9 is release hygiene → remained 0.1.0 (docs/test/governance only).
