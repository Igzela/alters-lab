# P11-M1 Route and Page Inventory

## Frontend Pages

| Page | Nav Key | Component File | Backend APIs Used | User-Facing Purpose | Status | Notes |
|------|---------|---------------|-------------------|---------------------|--------|-------|
| SystemStatus | status | SystemStatus.tsx | GET /product/status, GET /local-app/status, GET /runtime-layout/status, GET /provider-config/status | App health, route inventory, product status | usable | Reads 4 endpoints, displays system status |
| GettingStarted | getting-started | GettingStarted.tsx | (none — static content) | Onboarding checklist | usable | Static page, no API calls |
| WeeklyReview | weekly | WeeklyReview.tsx | POST /obsidian-weekly-note/ingest, GET /obsidian-weekly-note/list, POST /weekly-review/start, POST /weekly-review/{id}/complete, GET /weekly-review/list, POST /action-alignment/score, GET /action-alignment/list, GET /weekly-review-assistant/status, POST /weekly-review-assistant/suggest | 6-step weekly review flow: ingest note → start review → complete → score alignment | usable | Full workflow end-to-end in frontend |
| AlterDialogue | dialogue | AlterDialogue.tsx | GET /alter-dialogue/alters, GET /alter-dialogue/{alter_id}/context, POST /alter-dialogue/{alter_id}/reply | Alter dialogue with provider | partial | UI exists, backend read-only context, reply works if provider configured |
| RealityScore | reality | RealityScore.tsx | POST /calibration-loop/reality-scores | Submit reality score for calibration | partial | Form exists, submits score, but no calibration loop exercised |
| CalibrationHistory | history | CalibrationHistory.tsx | GET /calibration-loop/history, GET /weekly-review/list, GET /action-alignment/list | View calibration history, reviews, scores | partial | Lists data, no detail views or drill-down |
| RubricDelta | rubric | RubricDelta.tsx | POST /rubric-delta/suggest | View rubric delta suggestions | partial | Triggers suggest, displays result, no real suggestions in cold start |
| CheckpointPlan | checkpoint | CheckpointPlan.tsx | POST /checkpoint-regeneration/plan | View checkpoint regeneration plans | partial | Triggers plan, displays result, no real plans in cold start |
| ProviderSettings | provider | ProviderSettings.tsx | GET /provider-config/config, GET /provider-config/status, POST /provider-config/config, POST /provider-config/secret, DELETE /provider-config/secret, POST /provider-config/test | Configure provider, manage secrets, test connectivity | usable | Full CRUD, end-to-end |
| P6Progress | (panel in WeeklyReview) | P6Progress.tsx | GET /product/status | P6 state panel showing validation status | usable | Read-only panel, false flags correct |

## Backend Routes — Per-Route Inventory

### Runtime / Local App

| Method | Path | Purpose | R/W | Provider Risk | Frontend-Used | Status |
|--------|------|---------|-----|---------------|---------------|--------|
| GET | /local-app/health | Health check | read | none | no | route_exists |
| GET | /local-app/status | App status (pid, mode, port) | read | none | yes | verified_by_packaged_smoke |
| GET | /local-app/frontend-status | Frontend build status | read | none | no | route_exists |
| GET | /runtime-layout/health | Health check | read | none | no | route_exists |
| GET | /runtime-layout/status | Layout paths and mode | read | none | yes | verified_by_packaged_smoke |
| POST | /runtime-layout/ensure-config | Ensure config files exist | write | none | no | route_exists |
| GET | /storage-boundary/health | Health check | read | none | no | route_exists |
| GET | /storage-boundary/manifest | Storage path manifest | read | none | no | route_exists |

### Provider Config

| Method | Path | Purpose | R/W | Provider Risk | Frontend-Used | Status |
|--------|------|---------|-----|---------------|---------------|--------|
| GET | /provider-config/health | Health check | read | none | no | route_exists |
| GET | /provider-config/config | Get provider config (redacted) | read | none | yes | normal_user_ready |
| POST | /provider-config/config | Update provider config | write | none | yes | normal_user_ready |
| GET | /provider-config/status | Provider mode and status | read | none | yes | normal_user_ready |
| POST | /provider-config/secret | Store provider secret | write | none | yes | normal_user_ready |
| DELETE | /provider-config/secret | Delete provider secret | write | none | yes | normal_user_ready |
| POST | /provider-config/test | Test provider connectivity | read | mock/live_possible | yes | normal_user_ready |

### Provider Adapter / Connectivity / Gateway / Dialogue / Assistant

| Method | Path | Purpose | R/W | Provider Risk | Frontend-Used | Status |
|--------|------|---------|-----|---------------|---------------|--------|
| GET | /provider-adapter/health | Health check | read | none | no | route_exists |
| GET | /provider-adapter/status | Adapter status | read | none | no | route_exists |
| POST | /provider-adapter/preview | Preview adapter output | read | mock/live_possible | no | tested_by_backend_suite |
| GET | /provider-connectivity/health | Health check | read | none | no | route_exists |
| GET | /provider-connectivity/status | Connectivity status | read | none | no | route_exists |
| POST | /provider-connectivity/check | Check provider connectivity | read | mock/live_possible | no | tested_by_backend_suite |
| GET | /provider-gateway/health | Health check | read | none | no | route_exists |
| POST | /provider-gateway/complete | Complete via gateway | read | mock/live_possible | no | tested_by_backend_suite |
| GET | /provider-gateway/config-status | Gateway config status | read | none | no | route_exists |
| GET | /provider-dialogue/health | Health check | read | none | no | route_exists |
| POST | /provider-dialogue/{alter_id}/reply | Reply in alter dialogue | read | mock/live_possible | yes | partial |
| POST | /provider-dialogue-preview/generate | Generate dialogue preview | read | mock/live_possible | no | tested_by_backend_suite |
| GET | /provider-dialogue-preview/health | Health check | read | none | no | route_exists |
| GET | /provider-dialogue-preview/status | Preview status | read | none | no | route_exists |
| GET | /weekly-review-assistant/health | Health check | read | none | no | route_exists |
| GET | /weekly-review-assistant/status | Assistant status | read | none | yes | normal_user_ready |
| POST | /weekly-review-assistant/suggest | Get advisory suggestion | read | mock/live_possible | yes | partial |

### Obsidian Weekly Note

| Method | Path | Purpose | R/W | Provider Risk | Frontend-Used | Status |
|--------|------|---------|-----|---------------|---------------|--------|
| GET | /obsidian-weekly-note/health | Health check | read | none | no | route_exists |
| POST | /obsidian-weekly-note/ingest | Ingest raw weekly note | write | none | yes | normal_user_ready |
| GET | /obsidian-weekly-note/list | List weekly notes | read | none | yes | normal_user_ready |
| GET | /obsidian-weekly-note/{record_id} | Get single note | read | none | yes | normal_user_ready |
| POST | /obsidian-weekly-note/{record_id}/edit | Edit weekly note | write | none | yes | normal_user_ready |

### Weekly Review

| Method | Path | Purpose | R/W | Provider Risk | Frontend-Used | Status |
|--------|------|---------|-----|---------------|---------------|--------|
| GET | /weekly-review/health | Health check | read | none | no | route_exists |
| POST | /weekly-review/start | Start review session | write | none | yes | normal_user_ready |
| GET | /weekly-review/list | List review sessions | read | none | yes | normal_user_ready |
| GET | /weekly-review/{session_id} | Get review session | read | none | yes | normal_user_ready |
| POST | /weekly-review/{session_id}/complete | Complete review session | write | none | yes | normal_user_ready |

### Action Alignment

| Method | Path | Purpose | R/W | Provider Risk | Frontend-Used | Status |
|--------|------|---------|-----|---------------|---------------|--------|
| GET | /action-alignment/health | Health check | read | none | no | route_exists |
| POST | /action-alignment/score | Submit alignment score | write | none | yes | normal_user_ready |
| GET | /action-alignment/list | List scores | read | none | yes | normal_user_ready |
| GET | /action-alignment/{score_id} | Get score detail | read | none | yes | normal_user_ready |

### Pattern Review

| Method | Path | Purpose | R/W | Provider Risk | Frontend-Used | Status |
|--------|------|---------|-----|---------------|---------------|--------|
| GET | /pattern-review/health | Health check | read | none | no | route_exists |
| POST | /pattern-review/build | Build 4-week pattern | write | none | no | tested_by_backend_suite |
| GET | /pattern-review/list | List pattern reviews | read | none | no | tested_by_backend_suite |
| GET | /pattern-review/{review_id} | Get pattern review | read | none | no | tested_by_backend_suite |

### Weekly Reminder

| Method | Path | Purpose | R/W | Provider Risk | Frontend-Used | Status |
|--------|------|---------|-----|---------------|---------------|--------|
| GET | /weekly-reminder/health | Health check | read | none | no | route_exists |
| GET | /weekly-reminder/status | Reminder status | read | none | yes (P6Progress) | partial |
| POST | /weekly-reminder/complete | Mark reminder complete | write | none | no | tested_by_backend_suite |
| POST | /weekly-reminder/skip | Skip reminder with reason | write | none | no | tested_by_backend_suite |
| GET | /weekly-reminder/history | Reminder history | read | none | no | tested_by_backend_suite |

### Self-Deception Challenge

| Method | Path | Purpose | R/W | Provider Risk | Frontend-Used | Status |
|--------|------|---------|-----|---------------|---------------|--------|
| GET | /self-deception-challenge/health | Health check | read | none | no | route_exists |
| POST | /self-deception-challenge/evaluate | Evaluate self-deception risk | write | none | no | tested_by_backend_suite |
| GET | /self-deception-challenge/list | List challenges | read | none | no | tested_by_backend_suite |
| POST | /self-deception-challenge/edit-challenge | Edit challenge record | write | none | no | tested_by_backend_suite |

### Alter Recommendation

| Method | Path | Purpose | R/W | Provider Risk | Frontend-Used | Status |
|--------|------|---------|-----|---------------|---------------|--------|
| GET | /alter-recommendation/health | Health check | read | none | no | route_exists |
| POST | /alter-recommendation/recommend | Generate recommendation | write | none | no | tested_by_backend_suite |
| GET | /alter-recommendation/list | List recommendations | read | none | no | tested_by_backend_suite |
| POST | /alter-recommendation/{recommendation_id}/override | Override recommendation | write | none | no | tested_by_backend_suite |

### Behavior Validation

| Method | Path | Purpose | R/W | Provider Risk | Frontend-Used | Status |
|--------|------|---------|-----|---------------|---------------|--------|
| GET | /behavior-validation/health | Health check | read | none | no | route_exists |
| POST | /behavior-validation/evaluate | Evaluate behavior validation | write | none | no | tested_by_backend_suite |
| GET | /behavior-validation/report | Get validation report | read | none | no | tested_by_backend_suite |

### P6 Data Retention

| Method | Path | Purpose | R/W | Provider Risk | Frontend-Used | Status |
|--------|------|---------|-----|---------------|---------------|--------|
| GET | /p6-data-retention/health | Health check | read | none | no | route_exists |
| GET | /p6-data-retention/manifest | Record counts per area | read | none | no | tested_by_backend_suite |
| POST | /p6-data-retention/export | Export records | write | none | no | tested_by_backend_suite |
| POST | /p6-data-retention/delete | Delete a record | write | none | no | tested_by_backend_suite |
| POST | /p6-data-retention/archive | Archive records | write | none | no | tested_by_backend_suite |

### P6 Provider Policy

| Method | Path | Purpose | R/W | Provider Risk | Frontend-Used | Status |
|--------|------|---------|-----|---------------|---------------|--------|
| GET | /p6-provider-policy/health | Health check | read | none | no | route_exists |
| GET | /p6-provider-policy/status | Provider policy status | read | none | no | route_exists |
| POST | /p6-provider-policy/validate-config | Validate config against policy | read | none | no | tested_by_backend_suite |

### Alter Dialogue

| Method | Path | Purpose | R/W | Provider Risk | Frontend-Used | Status |
|--------|------|---------|-----|---------------|---------------|--------|
| GET | /alter-dialogue/health | Health check | read | none | no | route_exists |
| GET | /alter-dialogue/alters | List available alters | read | none | yes | partial |
| GET | /alter-dialogue/{alter_id}/context | Get dialogue context | read | none | yes | partial |
| POST | /alter-dialogue/{alter_id}/prompt | Send dialogue prompt | read | mock/live_possible | yes | partial |

### Calibration Loop

| Method | Path | Purpose | R/W | Provider Risk | Frontend-Used | Status |
|--------|------|---------|-----|---------------|---------------|--------|
| GET | /calibration-loop/health | Health check | read | none | no | route_exists |
| POST | /calibration-loop/reality-scores | Submit reality score | write | none | yes | partial |
| POST | /calibration-loop/drift/calculate | Calculate drift | read | none | no | tested_by_backend_suite |
| GET | /calibration-loop/history | Calibration history | read | none | yes | partial |

### Rubric Delta

| Method | Path | Purpose | R/W | Provider Risk | Frontend-Used | Status |
|--------|------|---------|-----|---------------|---------------|--------|
| GET | /rubric-delta/health | Health check | read | none | no | route_exists |
| POST | /rubric-delta/suggest | Generate delta suggestion | write | none | yes | partial |
| GET | /rubric-delta/list | List suggestions | read | none | no | tested_by_backend_suite |

### Archive Mechanism

| Method | Path | Purpose | R/W | Provider Risk | Frontend-Used | Status |
|--------|------|---------|-----|---------------|---------------|--------|
| GET | /archive-mechanism/health | Health check | read | none | no | route_exists |
| POST | /archive-mechanism/plan | Plan archive | write | none | no | tested_by_backend_suite |
| POST | /archive-mechanism/create | Create archive | write | none | no | tested_by_backend_suite |
| GET | /archive-mechanism/list | List archives | read | none | no | tested_by_backend_suite |

### Checkpoint Regeneration

| Method | Path | Purpose | R/W | Provider Risk | Frontend-Used | Status |
|--------|------|---------|-----|---------------|---------------|--------|
| GET | /checkpoint-regeneration/health | Health check | read | none | no | route_exists |
| POST | /checkpoint-regeneration/plan | Plan regeneration | write | none | yes | partial |
| GET | /checkpoint-regeneration/list | List plans | read | none | no | tested_by_backend_suite |

### Snapshot Intake

| Method | Path | Purpose | R/W | Provider Risk | Frontend-Used | Status |
|--------|------|---------|-----|---------------|---------------|--------|
| GET | /snapshot-intake/health | Health check | read | none | no | route_exists |
| POST | /snapshot-intake/sessions | Create intake session | write | none | no | tested_by_backend_suite |
| GET | /snapshot-intake/sessions/{session_id} | Get session | read | none | no | tested_by_backend_suite |
| POST | /snapshot-intake/sessions/{session_id}/answers | Submit answers | write | none | no | tested_by_backend_suite |
| POST | /snapshot-intake/sessions/{session_id}/confirm | Confirm intake | write | none | no | tested_by_backend_suite |
| GET | /snapshot-intake/sessions/{session_id}/next-anchor | Get next anchor | read | none | no | tested_by_backend_suite |
| POST | /snapshot-intake/sessions/{session_id}/persist | Persist snapshot | write | none | no | tested_by_backend_suite |

### Branches / Alters (Controlled Write)

| Method | Path | Purpose | R/W | Provider Risk | Frontend-Used | Status |
|--------|------|---------|-----|---------------|---------------|--------|
| GET | /branches/health | Health check | read | none | no | route_exists |
| POST | /branches/persist | Persist branches YAML | write | none | no | tested_by_backend_suite |
| GET | /alters/health | Health check | read | none | no | route_exists |
| POST | /alters/persist/{alter_id} | Persist alter YAML | write | none | no | tested_by_backend_suite |
| POST | /alters/persist-batch | Batch persist alters | write | none | no | tested_by_backend_suite |

### Generation / Draft / Promotion (Controlled Write Pipeline)

| Method | Path | Purpose | R/W | Provider Risk | Frontend-Used | Status |
|--------|------|---------|-----|---------------|---------------|--------|
| GET | /generation-drafts/health | Health check | read | none | no | route_exists |
| POST | /generation-drafts/preview | Generate draft | write | none | no | tested_by_backend_suite |
| GET | /generation-drafts/list | List drafts | read | none | no | tested_by_backend_suite |
| GET | /draft-review/health | Health check | read | none | no | route_exists |
| POST | /draft-review/{draft_id}/review | Review draft | write | none | no | tested_by_backend_suite |
| GET | /draft-review/list | List reviews | read | none | no | tested_by_backend_suite |
| GET | /promotion-orchestration/health | Health check | read | none | no | route_exists |
| POST | /promotion-orchestration/{draft_id}/plan | Plan promotion | write | none | no | tested_by_backend_suite |
| GET | /promotion-orchestration/list | List plans | read | none | no | tested_by_backend_suite |
| GET | /promotion-execution-gate/health | Health check | read | none | no | route_exists |
| POST | /promotion-execution-gate/{draft_id}/check | Check gate | read | none | no | tested_by_backend_suite |
| GET | /promotion-execution-gate/list | List gate checks | read | none | no | tested_by_backend_suite |
| GET | /promotion-live-execution/health | Health check | read | none | no | route_exists |
| POST | /promotion-live-execution/{draft_id}/run | Run live execution | write | none | no | tested_by_backend_suite |
| GET | /promotion-live-execution/list | List live executions | read | none | no | tested_by_backend_suite |

### Phase Closeout (Read-Only)

| Method | Path | Purpose | R/W | Provider Risk | Frontend-Used | Status |
|--------|------|---------|-----|---------------|---------------|--------|
| GET | /phase3-closeout/health | Health check | read | none | no | route_exists |
| GET | /phase3-closeout/report | Phase 3 closeout report | read | none | no | route_exists |
| GET | /phase3-closeout/evidence | Phase 3 evidence | read | none | no | route_exists |
| GET | /phase4-closeout/health | Health check | read | none | no | route_exists |
| GET | /phase4-closeout/report | Phase 4 closeout report | read | none | no | route_exists |
| GET | /phase4-closeout/evidence | Phase 4 evidence | read | none | no | route_exists |
| GET | /phase5-closeout/health | Health check | read | none | no | route_exists |
| GET | /phase5-closeout/report | Phase 5 closeout report | read | none | no | route_exists |
| GET | /phase5-closeout/evidence | Phase 5 evidence | read | none | no | route_exists |
| GET | /phase6-closeout/health | Health check | read | none | no | route_exists |
| GET | /phase6-closeout/report | Phase 6 closeout report | read | none | no | route_exists |
| GET | /phase6-closeout/evidence | Phase 6 evidence | read | none | no | route_exists |

### Product Surface / Infrastructure

| Method | Path | Purpose | R/W | Provider Risk | Frontend-Used | Status |
|--------|------|---------|-----|---------------|---------------|--------|
| GET | /product/health | Health check | read | none | no | route_exists |
| GET | /product/routes | Route inventory | read | none | yes | normal_user_ready |
| GET | /product/status | Product status | read | none | yes | normal_user_ready |
| GET | /product/workflow-capabilities | Workflow capabilities | read | none | no | route_exists |
| GET | /user-workflow/health | Health check | read | none | no | route_exists |
| GET | /user-workflow/state | Workflow state | read | none | no | tested_by_backend_suite |
| POST | /user-workflow/run-summary | Save workflow run | write | none | no | tested_by_backend_suite |
| GET | /cycle-summary/health | Health check | read | none | no | route_exists |
| GET | /cycle-summary/current | Current cycle | read | none | no | route_exists |
| GET | /cycle-summary/artifacts | Cycle artifacts | read | none | no | route_exists |
| GET | /cycle-summary/validation | Validation status | read | none | no | route_exists |
| GET | /evidence/health | Health check | read | none | no | route_exists |
| GET | /evidence/reports | Evidence reports | read | none | no | route_exists |
| GET | /evidence/status | Evidence status | read | none | no | route_exists |
| GET | /evidence/active-yaml-validation | Active YAML validation | read | none | no | route_exists |
| GET | /evidence/day30-demo | Day 30 demo | read | none | no | route_exists |
| GET | /evidence/phase1-closeout | Phase 1 closeout | read | none | no | route_exists |

### Static / Meta

| Method | Path | Purpose | R/W | Provider Risk | Frontend-Used | Status |
|--------|------|---------|-----|---------------|---------------|--------|
| GET | / | Root redirect | read | none | no | route_exists |
| GET | /health | Global health | read | none | no | route_exists |
| GET | /docs | Swagger UI | read | none | no | route_exists |
| GET | /redoc | ReDoc | read | none | no | route_exists |
| GET | /openapi.json | OpenAPI spec | read | none | no | route_exists |
| GET | /assets/{asset_path} | Static assets | read | none | yes | verified_by_packaged_smoke |
| GET | /{frontend_path} | SPA catch-all | read | none | yes | verified_by_packaged_smoke |

## Summary Statistics

- **Total backend routes**: 124 (excluding catch-all and meta)
- **Frontend-used routes**: ~25 (routes actually called from React pages)
- **normal_user_ready**: ~15 (verified end-to-end in packaged flow)
- **tested_by_backend_suite**: ~45 (pass tests but not exercised from frontend)
- **partial**: ~8 (routes exist and work but frontend UX incomplete)
- **route_exists**: ~56 (route registered, health/status only, or no frontend integration)
