# P10-M1: Local Installation Cutover Checklist

## Purpose

Operator checklist for cutting over from repo/dev workflow to the packaged local app as the primary personal-use workflow.

## Pre-Cutover State

- Latest accepted commit: 6f3b7d7 (P10-000-R1)
- P7 sealed as LOCAL_APP_RELEASE_CANDIDATE
- P8 sealed as REAL_PROVIDER_READY_LOCAL_APP
- P9 sealed
- P10-000 PASS
- P6: CODE_COMPLETE / NOT_VALIDATED / NOT_SEALED
- P6 validation not started

## A. Build Package

```bash
python tools/build_deb.py
# Expected artifact: dist/deb/alters-lab_0.1.0_amd64.deb
```

## B. Install Package

```bash
# Option 1: apt
sudo apt install ./dist/deb/alters-lab_0.1.0_amd64.deb

# Option 2: dpkg fallback
sudo dpkg -i dist/deb/alters-lab_0.1.0_amd64.deb
sudo apt -f install
```

## C. Confirm Packaged App (Not Repo/Dev Mode)

```bash
which alters-lab
alters-lab doctor --json
alters-lab status
```

Verify:
- Runtime mode: packaged
- App root: /opt/alters-lab
- Data paths: ~/.local/share/alters-lab
- Config: ~/.config/alters-lab/config.yaml
- Logs: ~/.local/state/alters-lab/logs
- No PYTHONPATH/dev launcher is being used

## D. Start and Open App

```bash
alters-lab start
alters-lab open
# Default URL: http://127.0.0.1:18790
```

Confirm:
- Frontend loads
- Getting Started page exists
- Provider Settings page exists
- Weekly Review page exists

## E. Provider Cutover

- Default provider: disabled
- Optionally switch to mock mode only
- No real provider calls during P10-M1
- No API key required
- Do not enter real API keys yet unless explicitly approved later

## F. Backup Readiness

```bash
alters-lab backup --dry-run --json
```

Confirm:
- Secrets excluded by default
- Output path valid
- No secrets in backup

## G. Personal Data Boundary

Do NOT commit:
- ~/.config/alters-lab
- ~/.local/share/alters-lab
- ~/.local/state/alters-lab
- Weekly notes

Repo evidence must be redacted summary only.

## H. Cutover Evidence

Capture locally, commit only redacted summary:
- install_status
- doctor_status
- app_launch_status
- provider_mode
- backup_dry_run_status
- p6_validation_started=false

See `P10_M1_CUTOVER_EVIDENCE_TEMPLATE.md` for the fillable template.
