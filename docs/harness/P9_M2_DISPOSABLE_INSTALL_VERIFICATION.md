# P9-M2: Disposable Install/Upgrade/Remove Verification

## Status: done

## Goal

Verify that install, upgrade, and remove work correctly in a disposable environment (fakeroot). Verify data preservation on upgrade, clean removal on uninstall, no secret leakage.

## Method

`tools/p9_package_lifecycle_smoke.py` runs a full dpkg lifecycle in a disposable fakeroot:

1. **Install**: `dpkg --instdir=<fakeroot> --admindir=<fakeroot>/var/lib/dpkg -i <deb>`
2. **Upgrade**: Reinstall same .deb to trigger upgrade path
3. **Remove**: `dpkg --instdir=<fakeroot> --admindir=<fakeroot>/var/lib/dpkg -r alters-lab`

No host mutation. No sudo. No real provider calls.

## What It Verifies

| Phase | Check |
|---|---|
| Install | dpkg returns 0, package files exist in fakeroot |
| Install | postinst script runs without error |
| Upgrade | dpkg returns 0, user data (config, secrets, data dir) preserved |
| Upgrade | Secrets file mode preserved (0600) |
| Remove | dpkg returns 0, package files removed from fakeroot |
| Remove | User data preserved after remove (config, secrets, data, product) |
| Remove | postrm script runs without error |
| All | No host filesystem mutation outside temp directory |
| All | No real provider calls |
| All | p6_behavior_validated=False, p6_sealed=False |

## Evidence Redaction

- Temp root paths replaced with `[temp-root]`
- Sensitive fields (api_key, key_name, output_preview, suggestion, prompt) redacted
- Provider output patterns matched and replaced

## Hard Boundaries

- No changes to `alters/current/**`
- No changes to `alters/calibration/rubric.yaml`
- No runtime records committed
- No secrets committed
- No real provider calls
- No P6 validation claims
- No host sudo install/remove

## Test Coverage

`apps/api/tests/test_p9_package_lifecycle_smoke.py` covers:

- Argument parsing (required --deb, --json, --keep-temp, --evidence, defaults)
- Temp path redaction (strings, dicts, lists, non-matching preservation)
- Sensitive field redaction (api_key, key_name, output_preview, suggestion, nested, safety flag preservation, provider output patterns)
- Report contract assertions (valid report, install failure, upgrade data loss, remove secret loss, p6 true, host mutation, provider calls)
- Safety flags (smoke note is synthetic, report fields)

## Usage

```bash
# Build package first
python3 tools/build_deb.py

# Run lifecycle smoke
python3 tools/p9_package_lifecycle_smoke.py --deb dist/deb/alters-lab_0.1.0_amd64.deb --json

# Run with evidence file
python3 tools/p9_package_lifecycle_smoke.py --deb dist/deb/alters-lab_0.1.0_amd64.deb --json --evidence docs/harness/P9_M2_EVIDENCE.json

# Keep temp directory for debugging
python3 tools/p9_package_lifecycle_smoke.py --deb dist/deb/alters-lab_0.1.0_amd64.deb --json --keep-temp
```
