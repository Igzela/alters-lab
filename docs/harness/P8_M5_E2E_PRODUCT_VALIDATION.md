# P8-M5 E2E Product Validation

## Summary

Validates the full local app product path after P8 provider features. Package-context isolated HOME smoke by default; live provider checks optional and explicitly gated.

## Architecture

```
tools/p8_e2e_product_smoke.py
    → dpkg-deb -x into isolated temp install root
    → isolated HOME (config, data, state)
    → start packaged app server
    → validate routes (10 endpoints)
    → provider config smoke (disable→mock→test)
    → provider adapter smoke (mock preview)
    → provider connectivity smoke (dry-run check)
    → provider dialogue preview smoke (dry-run generate)
    → weekly review assistant smoke (dry-run suggest)
    → weekly review flow (ingest→start→suggest→complete→score)
    → backup/data safety smoke (dry-run backup)
    → stop server, cleanup
    → JSON summary + optional evidence file
```

## Files

| File | Purpose |
|------|---------|
| `tools/p8_e2e_product_smoke.py` | E2E smoke script with package-context isolated HOME |
| `apps/api/tests/test_p8_e2e_product_smoke.py` | 15 tests for smoke script defaults, contract, safety |
| `docs/harness/P8_M5_E2E_PRODUCT_VALIDATION_EVIDENCE.json` | Redacted JSON evidence from smoke run |

## Smoke Sections

| Section | What it validates |
|---------|-------------------|
| A. Package build | .deb artifact exists |
| B. Package extract | dpkg-deb -x into isolated root |
| C. Isolated HOME | config/data/state under temp HOME |
| D. Server start | packaged app starts and responds |
| E. Route validation | 10 key routes return 200 |
| F. Provider config | disable→mock→test, no network |
| G. Provider adapter | mock preview, no network, no YAML writes |
| H. Provider connectivity | dry-run check, no network |
| I. Dialogue preview | dry-run generate, unverified label, no persistence |
| J. Weekly assistant | dry-run suggest, unverified label, no persistence |
| K. Weekly review flow | ingest→start→suggest→complete→score with synthetic data |
| L. Backup/data safety | dry-run backup, secrets excluded |
| M. Final safety | P6 false flags, no active YAML, no secrets |

## Safety Guarantees

| Guarantee | Enforcement |
|-----------|-------------|
| No live provider by default | --allow-live-provider flag required |
| No sudo install | dpkg-deb -x only |
| Isolated HOME | temp directory, cleaned after run |
| No real secrets | evidence redacted, no key in output |
| P6 false flags | p6_behavior_validated=False, p6_sealed=False |
| No active YAML modified | git diff clean |
| Synthetic data only | SMOKE_NOTE explicitly synthetic |

## Optional Live Provider

The smoke script supports optional live provider flags:
- `--allow-live-provider`
- `--live-provider-confirmation run-live-p8-e2e-provider-smoke`

These are never invoked by default and require explicit human invocation.
