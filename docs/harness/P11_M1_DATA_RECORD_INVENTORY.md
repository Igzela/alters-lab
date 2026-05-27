# P11-M1 Data Record / Local Storage Inventory

## Storage Layout

### Dev Mode
```
repo_root/
  alters/product/
    config/          — config.yaml, secrets.yaml
    state/           — alters-lab.pid, logs/
    weekly_notes/    — weekly_note_*.yaml
    weekly_reviews/  — weekly_review_*.yaml
    calibration_records/ — action_alignment_*.yaml
    self_deception_challenges/ — self_deception_*.yaml
    alter_recommendations/ — alter_recommendation_*.yaml
    reminders/       — weekly_reminder_*.yaml
    pattern_reviews/ — pattern_review_*.yaml
    behavior_validation/ — behavior_validation_*.yaml
    exports/         — export_*.yaml, archive_*.yaml
```

### Packaged Mode
```
~/.config/alters-lab/   — config.yaml, secrets.yaml
~/.local/share/alters-lab/product/ — same subdirs as dev mode
~/.local/state/alters-lab/ — pid, logs/
```

## Record Types (20 record/config/state types)

| Record Type | Storage Area | Dev Path | Packaged Path | Create API | Read/List API | Delete API | Frontend Access | Packaged Mode | Status |
|-------------|-------------|----------|---------------|------------|---------------|------------|-----------------|---------------|--------|
| Weekly Notes | weekly_notes | alters/product/weekly_notes/*.yaml | ~/.local/share/alters-lab/product/weekly_notes/*.yaml | POST /obsidian-weekly-note/ingest | GET /obsidian-weekly-note/list, GET /obsidian-weekly-note/{record_id} | (none) | usable (WeeklyReview page: list, ingest, edit) | works | usable |
| Weekly Reviews | weekly_reviews | alters/product/weekly_reviews/*.yaml | ~/.local/share/alters-lab/product/weekly_reviews/*.yaml | POST /weekly-review/start, POST /weekly-review/{session_id}/complete | GET /weekly-review/list, GET /weekly-review/{session_id} | (none) | usable (WeeklyReview page: list, start, complete) | works | usable |
| Calibration Records (Action Alignment Scores) | calibration_records | alters/product/calibration_records/*.yaml | ~/.local/share/alters-lab/product/calibration_records/*.yaml | POST /action-alignment/score | GET /action-alignment/list, GET /action-alignment/{score_id} | (none) | partial (CalibrationHistory page: list only, no score detail view) | works | partial |
| Self-Deception Challenges | self_deception_challenges | alters/product/self_deception_challenges/*.yaml | ~/.local/share/alters-lab/product/self_deception_challenges/*.yaml | POST /self-deception-challenge/evaluate | GET /self-deception-challenge/list | (none) | missing (no frontend page) | works | partial |
| Alter Recommendations | alter_recommendations | alters/product/alter_recommendations/*.yaml | ~/.local/share/alters-lab/product/alter_recommendations/*.yaml | POST /alter-recommendation/recommend | GET /alter-recommendation/list, POST /alter-recommendation/{id}/override | (none) | missing (no frontend page) | works | partial |
| Weekly Reminders | reminders | alters/product/reminders/*.yaml | ~/.local/share/alters-lab/product/reminders/*.yaml | POST /weekly-reminder/complete, POST /weekly-reminder/skip | GET /weekly-reminder/status, GET /weekly-reminder/history | (none) | partial (P6Progress panel shows reminder state) | works | partial |
| Pattern Reviews | pattern_reviews | alters/product/pattern_reviews/*.yaml | ~/.local/share/alters-lab/product/pattern_reviews/*.yaml | POST /pattern-review/build | GET /pattern-review/list, GET /pattern-review/{review_id} | (none) | missing (no frontend page) | works | partial |
| Behavior Validation | behavior_validation | alters/product/behavior_validation/*.yaml | ~/.local/share/alters-lab/product/behavior_validation/*.yaml | POST /behavior-validation/evaluate | GET /behavior-validation/report | (none) | missing (no frontend page) | works | partial |
| Exports | exports | alters/product/exports/*.yaml | ~/.local/share/alters-lab/product/exports/*.yaml | POST /p6-data-retention/export, POST /p6-data-retention/archive | GET /p6-data-retention/manifest | POST /p6-data-retention/delete | missing (no frontend page) | works | partial |
| Provider Config | config_dir | alters/product/config/config.yaml | ~/.config/alters-lab/config.yaml | POST /provider-config/config | GET /provider-config/config, GET /provider-config/status | (none) | usable (ProviderSettings page: full CRUD) | works | usable |
| Provider Secrets | config_dir | alters/product/config/secrets.yaml | ~/.config/alters-lab/secrets.yaml | POST /provider-config/secret | GET /provider-config/status (redacted) | DELETE /provider-config/secret | usable (ProviderSettings page) | works | usable |
| App Config | config_dir | alters/product/config/config.yaml | ~/.config/alters-lab/config.yaml | (runtime_layout write_user_config) | GET /runtime-layout/status | (none) | partial (SystemStatus shows layout, no config edit UI) | works | partial |
| State (PID) | state_dir | alters/product/state/alters-lab.pid | ~/.local/state/alters-lab/alters-lab.pid | local_launcher.write_pid_file | local_launcher.read_pid_file | (none) | missing (internal only) | works | route_exists |
| Logs | state_dir | alters/product/state/logs/ | ~/.local/state/alters-lab/logs/ | local_launcher (server log) | (none) | (none) | missing (no frontend log viewer) | works | route_exists |
| Generation Drafts | (in-memory + draft workspace) | alters/product/drafts/ (if persisted) | same | POST /generation-drafts/preview | GET /generation-drafts/list | (none) | missing (no frontend page) | works | partial |
| Orchestration Plans | (draft workspace) | alters/product/promotion_plans/ (if persisted) | same | POST /promotion-orchestration/{id}/plan | GET /promotion-orchestration/list | (none) | missing (no frontend page) | works | route_exists |
| Gate Reports | (draft workspace) | alters/product/gate_reports/ (if persisted) | same | POST /promotion-execution-gate/{id}/check | GET /promotion-execution-gate/list | (none) | missing (no frontend page) | works | route_exists |
| Live Execution Reports | (draft workspace) | alters/product/live_executions/ (if persisted) | same | POST /promotion-live-execution/{id}/run | GET /promotion-live-execution/list | (none) | missing (no frontend page) | works | route_exists |
| Phase Closeout Reports | (repo artifacts) | docs/harness/ closeout reports | N/A (dev only) | phase*_closeout routers | phase*_closeout routers | (none) | missing (no frontend page) | works | route_exists |
| Workflow Run Summaries | state_dir | alters/product/state/ (workflow summary files) | ~/.local/state/alters-lab/ | POST /user-workflow/run-summary | GET /user-workflow/state | (none) | missing (no frontend page) | works | route_exists |

## Key Observations

1. **All P6 runtime records use YAML files** via `p6_runtime.py` read/write/list/delete helpers. No database.
2. **Record format**: `{record_id}.yaml` per file, directories per area.
3. **Provider secrets** stored in `secrets.yaml` (0600 permissions), redacted in all API responses.
4. **No frontend pages** for: self-deception challenges, alter recommendations, pattern reviews, behavior validation, exports, generation drafts, orchestration plans, gate reports, live execution reports, phase closeouts, workflow summaries.
5. **CalibrationHistory page** lists scores but has no detail view or drill-down.
6. **Packaged mode** uses `~/.local/share/alters-lab/product/` for all record storage; config in `~/.config/alters-lab/`.
7. **No record type has a delete API** exposed to the frontend except provider secrets (DELETE /provider-config/secret).
