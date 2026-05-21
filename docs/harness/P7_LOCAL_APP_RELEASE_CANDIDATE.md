# P7 Local App Release Candidate

## Status

P7-M8 status: **PASS**

This release-candidate check validates the Debian package as an independent local app using a simulated package install with `dpkg-deb -x` and an isolated `HOME`. It does not install into the operator's real system, does not write real user data, and does not create P6 real-use evidence.

P6 remains: **CODE_COMPLETE / NOT_VALIDATED / NOT_SEALED**.

## Method

- Built frontend production assets.
- Built `dist/deb/alters-lab_0.1.0_amd64.deb`.
- Inspected package contents and maintainer scripts with `tools/inspect_deb_safety.py`.
- Extracted the `.deb` into a temporary package root.
- Started the packaged CLI with:
  - `ALTERS_LAB_MODE=packaged`
  - `ALTERS_LAB_APP_ROOT=[temp-root]/pkgroot/opt/alters-lab`
  - isolated `HOME=[temp-root]/home`
- Opened local app endpoints over `127.0.0.1`.
- Loaded the built frontend index and bundled asset from FastAPI.
- Configured provider mode to `mock` through local API.
- Ran a synthetic weekly review flow to verify packaged write paths only.
- Ran backup dry-run.
- Stopped the server and deleted the temporary smoke HOME.

## Verification Results

| Check | Result |
|-------|--------|
| Backend tests | PASS, 949 tests |
| Frontend build | PASS |
| Debian package build | PASS |
| Package safety inspection | PASS |
| Package-context launcher status/doctor/start/stop | PASS |
| Local app health/status | PASS |
| Frontend served by FastAPI | PASS |
| Provider status/config/test redacted | PASS |
| Synthetic weekly note/review/calibration records under isolated user data dir | PASS |
| Backup dry-run excludes secrets/logs by default | PASS |
| P6 behavior validation flag | false |
| P6 sealed flag | false |

## Runtime Layout Observed

The smoke test used packaged mode with an isolated user home. Runtime records were written below:

- `[temp-root]/home/.local/share/alters-lab/product/weekly_notes/`
- `[temp-root]/home/.local/share/alters-lab/product/weekly_reviews/`
- `[temp-root]/home/.local/share/alters-lab/product/calibration_records/`

Config/log paths resolved below:

- `[temp-root]/home/.config/alters-lab/config.yaml`
- `[temp-root]/home/.local/state/alters-lab/logs/`

These paths prove packaged mode no longer requires repo runtime paths for local app use.

## Evidence Artifacts

- `docs/harness/P7_M8_RELEASE_CANDIDATE_EVIDENCE.json`
- `tools/p7_local_app_smoke.py`
- `tools/inspect_deb_safety.py`

## Boundary Confirmations

- No active YAML was changed.
- `alters/calibration/rubric.yaml` was not changed.
- No raw P6 runtime records were staged or committed.
- Provider stayed disabled/mock unless explicitly configured.
- Provider dry-run made no network call.
- Provider secrets were not returned by API responses.
- Synthetic smoke records were created only inside a temporary HOME and deleted after the run.
- P7 did not mark P6 behavior validated.
- P7 did not seal P6.
- P8 remains blocked.

## Next Step

P7-M9: produce P7 closeout evidence from the release-candidate results while preserving the P6 validation boundary.
