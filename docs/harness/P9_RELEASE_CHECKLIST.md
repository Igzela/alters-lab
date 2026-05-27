# P9 Release Checklist

Use this checklist before any release (tag, .deb publish, or personal deployment).

## Pre-Release Checks

### Backend Tests

```bash
PYTHONPATH=apps/api/src python3 -m pytest apps/api/tests/ -q
```

Must pass with 0 failures.

### Frontend Build

```bash
cd apps/web && npm run build
```

Must complete without errors.

### Package Build

```bash
python3 tools/build_deb.py
```

Must produce `dist/deb/alters-lab_0.1.0_amd64.deb` (or current version).

### Package Safety Inspection

```bash
python3 tools/inspect_deb_safety.py dist/deb/alters-lab_<version>_amd64.deb --json
```

Status must be `PASS`. Checks: required paths present, forbidden paths absent.

### Package Lifecycle Smoke

```bash
python3 tools/p9_package_lifecycle_smoke.py --deb dist/deb/alters-lab_<version>_amd64.deb --json
```

All sections must PASS. Verifies: install, upgrade, remove, data preservation, secret preservation.

### Forbidden Claims Check

```bash
grep -rn "P6.*validated\|P6.*sealed\|P6.*passed" apps/api/src/ docs/user/ --include="*.py" --include="*.md" | grep -vi "not.*validated\|not.*sealed\|NOT_VALIDATED\|NOT_SEALED\|not behavior-validated\|not sealed\|code complete but not\|remains.*NOT\|is not\|does not\|cannot\|unvalidated\|unsealed"
```

Must return no results. P6 must not be claimed as validated or sealed.

### Secret Check

```bash
grep -rn "sk-\|api_key.*=.*['\"]" apps/api/src/ apps/web/src/ --include="*.py" --include="*.ts" --include="*.tsx" | grep -v "test\|_test\|mock\|example\|placeholder\|redact\|never\|type=\"password\"\|autocomplete"
```

Must return no results. No real API keys in source.

### Doctor Output Review

```bash
alters-lab doctor --json
```

Review output: all checks PASS or WARN (no BLOCKED unless understood), actionable messages, no secrets leaked.

## Documentation Checks

- [ ] INSTALL.md is current
- [ ] FIRST_RUN.md is current
- [ ] FIRST_RUN_CHECKLIST.md is current
- [ ] PROVIDER_SETUP.md is current
- [ ] PROVIDER_SAFETY.md is current
- [ ] TROUBLESHOOTING.md is current
- [ ] DATA_AND_BACKUP.md is current
- [ ] UNINSTALL.md is current
- [ ] README.md Documentation section links work

## Governance Checks

- [ ] PROJECT_BOARD.md reflects current phase state
- [ ] TASK_QUEUE.md reflects current milestone statuses
- [ ] START_HERE_FOR_NEW_SESSION.md is current
- [ ] CURRENT_SESSION_CONTEXT.md is current
- [ ] RUN_LOG.md has latest entries
- [ ] EVIDENCE_INDEX.md has latest entries

## Post-Release

- [ ] Tag the release commit
- [ ] Verify the .deb installs on a clean system (or disposable environment)
- [ ] Verify `alters-lab doctor` passes after install
- [ ] Verify `alters-lab start` opens the app
