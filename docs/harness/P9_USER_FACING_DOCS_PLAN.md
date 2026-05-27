# P9 User-Facing Docs Plan

## Documents to Create

### 1. Install / Launch / Uninstall Guide (P9-M1)

Location: `docs/INSTALL.md`

Contents:
- System requirements (Linux, Python 3.10+)
- How to install from .deb package (`sudo dpkg -i alters-lab_*.deb`)
- How to launch (`alters-lab start`)
- How to check status (`alters-lab status`)
- How to stop (`alters-lab stop`)
- How to uninstall (`sudo dpkg -r alters-lab`)
- Where data is stored (`~/.local/share/alters-lab/`)
- Where config is stored (`~/.config/alters-lab/`)
- Where logs are stored (`~/.local/state/alters-lab/logs/`)

### 2. First-Run Onboarding Guide (P9-M3)

Location: `docs/FIRST_RUN.md`

Contents:
- What is Alters Lab?
- What is P6/P7/P8?
- How to configure a mock provider
- How to run your first weekly review
- How to interpret the results
- What the safety boundaries mean

### 3. Provider Setup Guide (P9-M4)

Location: `docs/PROVIDER_SETUP.md`

Contents:
- What is a provider?
- Mock vs live provider
- How to configure a live provider (API key, base URL, model)
- Safety model: confirmation gating, output labeling
- What the provider can and cannot do
- Troubleshooting provider issues

### 4. Troubleshooting Guide (P9-M5)

Location: `docs/TROUBLESHOOTING.md`

Contents:
- Common issues and solutions
- How to run `alters-lab doctor`
- How to check logs
- How to reset config
- How to report issues

### 5. Release Checklist (P9-M6)

Location: `docs/harness/RELEASE_CHECKLIST.md`

Contents:
- Backend tests pass
- Frontend build passes
- Package builds
- Package safety inspection passes
- P7 smoke passes
- P8 smoke passes
- Provider safety audit passes
- Docs updated
- Version bumped
- Changelog updated

## Existing Docs to Update

- `README.md` — update with install instructions and current state
- `docs/PROVIDER_CONFIGURATION.md` — verify accuracy against current implementation
- `apps/api/README.md` — verify accuracy

## Doc Review Process

For each document:
1. Write the doc
2. Test the instructions against actual CLI behavior
3. Verify accuracy of paths, commands, and expected outputs
4. Get GPT/human review
