# Provider Safety

This document describes how Alters Lab handles provider secrets, output, and safety boundaries.

## Secret Storage

### Config vs Secrets

- `~/.config/alters-lab/config.yaml` stores **non-secret** provider configuration only (mode, base URL, model, timeout, storage preference)
- `~/.config/alters-lab/secrets.yaml` stores API keys as a fallback (chmod 0600)
- **Keyring** is the preferred secret storage when available

### API Key Handling

- API keys are **never returned** by any API endpoint
- API keys are **never displayed** after initial storage
- API keys are **never logged**
- API keys are **never included** in backup archives by default
- The API key input field uses `type="password"` and `autocomplete="off"`

### Backup Behavior

`alters-lab backup` **excludes secrets by default**. To include secrets in a backup, you must explicitly pass `--include-secrets --confirm-include-secrets`.

## Provider Output Safety

Provider output (dialogue responses, weekly review suggestions) is subject to strict safety boundaries:

### What Provider Output CANNOT Do

- **Cannot write active YAML** — provider output cannot modify `alters/current/**`
- **Cannot write rubric** — provider output cannot modify `alters/calibration/rubric.yaml`
- **Cannot create reality scores** — reality scores are user-submitted only
- **Cannot create action alignment scores** — action alignment scores are user-submitted only
- **Cannot auto-complete weekly reviews** — reviews require manual user completion
- **Cannot persist by default** — provider output is displayed as preview only

### What Provider Output IS

- **Unverified** — all provider output is labeled as unverified
- **Advisory only** — provider suggestions are recommendations, not decisions
- **User-managed** — you decide what to copy, edit, and submit

## Confirmation Gating

Every provider network call requires explicit user confirmation:

| Action | Network Call | Confirmation Required |
|--------|-------------|----------------------|
| Dry-run config/provider test | No | Explicit click (local check only) |
| Live connectivity check | Yes (may call `/models`) | Exact confirmation string |
| Dialogue live preview | Yes (may send explicit prompt) | Exact confirmation string |
| Weekly assistant live suggestion | Yes (may send selected/request context) | Exact confirmation string |

Dry-run verifies local configuration shape and readiness — it makes no provider network call. No provider call happens automatically or in the background.

## Network Behavior

- **Disabled mode**: No network calls
- **Mock mode**: No network calls (simulated responses)
- **openai-compatible-http mode**: Network calls only to the user-configured base URL

The app does not phone home, send telemetry, or contact any server other than your configured provider endpoint.

## P6 Boundary

P6 (Personal Long-Term Use Hardening) is **code complete but not behavior-validated and not sealed**. Provider output does not constitute P6 validation. P6 validation requires 4 weeks of real use with actual weekly notes — this has not started.

Provider suggestions are not a substitute for human judgment in the calibration process.
