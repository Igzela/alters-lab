# P7-R1 Frontend Usability Layer

## Status

P7-R1 status: **PASS**

This slice adds the missing P6 weekly review frontend handoff so the local app can be used for real weekly review evidence without Codex, Claude Code, curl, pytest, or helper scripts.

P6 remains: **CODE_COMPLETE / NOT_VALIDATED / NOT_SEALED**.

P8 remains: **blocked**.

## Product Change

The local app now has a `Weekly Review` page in the main navigation. It is the primary P6 entry point for real weekly review usage.

The page supports:

- Paste weekly note from Obsidian-style template.
- Ingest note through `/obsidian-weekly-note/ingest`.
- Review extracted record and preserve raw-note status.
- Edit extracted fields through `/obsidian-weekly-note/{record_id}/edit` only with `correction_note`.
- Start weekly review session through `/weekly-review/start`.
- Complete weekly review through `/weekly-review/{session_id}/complete`.
- Submit action alignment score through `/action-alignment/score`.
- Show completion summary with weekly note ID, review session ID, score ID, score value, and explicit P6 false flags.

## P6 Progress

The Weekly Review page includes a P6 progress panel that reads:

- `/obsidian-weekly-note/list`
- `/weekly-review/list`
- `/action-alignment/list`

It shows weekly notes, weekly reviews, action alignment records, approximate week progress, missing requirements, and fixed boundary text:

- P6 behavior validated: false
- P6 sealed: false

It does not run behavior validation and does not claim validation.

## Related Usability Fixes

- Status page now shows local app mode, config path, product data dir, frontend availability, provider mode, and P6 state.
- Status page includes a `Start Weekly Review` button.
- Provider Settings now tracks unsaved config changes and disables provider test until config is saved.
- Reality Score now explains it is manual score submission, not the weekly review entry point, and links to Weekly Review.
- History now includes weekly review and action alignment records alongside existing calibration history.

## API Calls Wired

- `POST /obsidian-weekly-note/ingest`
- `GET /obsidian-weekly-note/list`
- `POST /obsidian-weekly-note/{record_id}/edit`
- `POST /weekly-review/start`
- `GET /weekly-review/list`
- `POST /weekly-review/{session_id}/complete`
- `POST /action-alignment/score`
- `GET /action-alignment/list`
- `GET /provider-config/status`
- `GET /runtime-layout/status`
- `GET /local-app/status`

## Verification

| Check | Result |
|-------|--------|
| Frontend build | PASS |
| Backend tests | PASS |
| Debian package build | PASS |
| Active YAML diff | empty |
| Rubric diff | empty |
| Runtime records | none staged |
| Generated frontend/package outputs | ignored |
| Secret scan | no real secrets |

## Boundaries

- No `alters/current/**` changes.
- No `alters/calibration/rubric.yaml` changes.
- No raw runtime records committed.
- No provider secrets committed.
- No live provider calls added.
- No provider output writes active YAML.
- No provider output generates reality scores.
- No P6 behavior validation claim.
- No P6 seal claim.
- P8 not started.

## Remaining Gaps

- P6 pattern review still needs its own friendly frontend later.
- Actual four-week validation still requires real usage over time.
- No heavy frontend test framework was introduced; verification uses TypeScript/Vite build.
