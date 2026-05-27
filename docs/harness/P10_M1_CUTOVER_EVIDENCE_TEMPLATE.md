# P10-M1 Cutover Evidence Template

Fill this template after completing the cutover checklist. Commit the redacted version to the repo.

```yaml
p10_m1_cutover:
  date: YYYY-MM-DD
  package_artifact: dist/deb/alters-lab_0.1.0_amd64.deb
  install_status: PASS/FAIL
  doctor_status: PASS/FAIL
  runtime_mode: packaged
  app_root: /opt/alters-lab
  frontend_loaded: true/false
  provider_mode: disabled/mock
  backup_dry_run_status: PASS/FAIL
  p6_validation_started: false
  p6_sealed: false
  personal_content_committed: false
  secrets_committed: false
  notes: ""
```

## Warnings

- Do NOT paste raw weekly notes.
- Do NOT paste API keys.
- Do NOT paste raw provider prompts/responses.
- Do NOT paste full logs unless reviewed/redacted.
- Only redacted summaries go into the repo.
