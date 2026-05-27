# P11-M1: Current App Capability Inventory

> **R1 update**: This inventory has been refined. See also:
> - `P11_M1_DATA_RECORD_INVENTORY.md` — data record / local storage inventory
> - `P11_M1_ROUTE_AND_PAGE_INVENTORY.md` — per-route granularity with method, path, read/write, provider risk, frontend-used, status
> - `P11_M1_USER_WORKFLOW_INVENTORY.md` — per-workflow detail with frontend path, APIs, records, gaps

## Frontend Pages (9 pages + 1 panel)

| Page | Route Key | File | Status | Notes |
|------|-----------|------|--------|-------|
| SystemStatus | status | SystemStatus.tsx | usable | Health, route inventory, product status |
| WeeklyReview | weekly | WeeklyReview.tsx | usable | 6-step flow: ingest → start → review → complete → score. Provider suggestion optional |
| AlterDialogue | dialogue | AlterDialogue.tsx | partial | UI exists, backend read-only, no real provider dialogue flow |
| RealityScore | reality | RealityScore.tsx | partial | Score submission form, but no real calibration loop exercised |
| CalibrationHistory | history | CalibrationHistory.tsx | partial | History display, no real records to show |
| RubricDelta | rubric | RubricDelta.tsx | partial | Delta suggestions display, no real suggestions |
| CheckpointPlan | checkpoint | CheckpointPlan.tsx | partial | Plan display, no real plans |
| ProviderSettings | provider | ProviderSettings.tsx | usable | Config, secret, test, safety notes. Works end-to-end |
| GettingStarted | getting-started | GettingStarted.tsx | usable | Static onboarding checklist |
| P6Progress | (panel) | P6Progress.tsx | usable | P6 state panel in WeeklyReview, false flags correct |

## Backend Routes (124 endpoints across 30+ route groups)

> 124 backend routes exist and are grouped; functional readiness varies by workflow and frontend integration. See `P11_M1_ROUTE_AND_PAGE_INVENTORY.md` for per-route method, path, read/write classification, provider risk, frontend-used, and status.

### Core P6 Workflow Routes

| Group | Endpoints | Status | Notes |
|-------|-----------|--------|-------|
| Obsidian Weekly Note | health, ingest, list, get, edit | usable | Full CRUD for weekly notes |
| Weekly Review | health, start, list, get, complete | usable | Full session lifecycle |
| Action Alignment | health, score, list, get | usable | Score submission and retrieval |
| Alter Recommendation | health, recommend, list, override | usable | Deterministic alter recommendation |
| Self-Deception Challenge | health, evaluate, list, edit-challenge | usable | Self-deception risk evaluation |
| Pattern Review | health, build, list, get | usable | 4-week pattern detection |
| Weekly Reminder | health, status, complete, skip, history | usable | Reminder state management |
| Behavior Validation | health, evaluate, report | usable | P6 behavior validation gate |
| P6 Data Retention | health, manifest, export, delete, archive | usable | Data retention controls |
| P6 Provider Policy | health, status, validate-config | usable | Provider policy check |

### Provider Routes

| Group | Endpoints | Status | Notes |
|-------|-----------|--------|-------|
| Provider Config | health, status, config, secret (CRUD), test | usable | Full config management |
| Provider Gateway | health, complete, config-status | usable | Mock/disabled/openai modes |
| Provider Adapter | health, status, preview | usable | Adapter contract |
| Provider Connectivity | health, status, check | usable | Connectivity check |
| Provider Dialogue Preview | health, status, generate | usable | Dialogue preview |
| Provider Dialogue | health, reply | usable | Alter dialogue with provider |
| Weekly Review Assistant | health, status, suggest | usable | Advisory suggestions |

### Phase 3-5 Routes (Controlled Write / Closeout)

| Group | Endpoints | Status | Notes |
|-------|-----------|--------|-------|
| Snapshot Intake | health, create, get, next-anchor, answer, confirm, persist | usable | Full intake flow |
| Branches | health, persist | usable | Controlled write |
| Alters | health, persist, persist-batch | usable | Controlled write |
| Generation Drafts | health, preview, list | usable | Draft generation |
| Draft Review | health, review, list | usable | Review boundary |
| Promotion Orchestration | health, plan, list | usable | Orchestration planning |
| Promotion Execution Gate | health, check, list | usable | Execution gate |
| Promotion Live Execution | health, run, list | usable | Live execution |
| Phase 3/4/5/6 Closeout | health, report, evidence | usable | Read-only closeout |

### Calibration Routes

| Group | Endpoints | Status | Notes |
|-------|-----------|--------|-------|
| Calibration Loop | health, reality-scores, drift/calculate, history | usable | Score submission and drift |
| Rubric Delta | health, suggest, list | usable | Delta suggestions |
| Archive Mechanism | health, plan, create, list | usable | Archive planning |
| Checkpoint Regeneration | health, plan, list | usable | Regeneration planning |

### Infrastructure Routes

| Group | Endpoints | Status | Notes |
|-------|-----------|--------|-------|
| Runtime Layout | health, status, ensure-config | usable | Dev/packaged detection |
| Local App | health, status, frontend-status | usable | App status |
| Storage Boundary | health, manifest | usable | Path classification |
| User Workflow | health, state, run-summary | usable | Workflow state |
| Product Surface | health, routes, status, workflow-capabilities | usable | Product inventory |
| Cycle Summary | health, current, artifacts, validation | usable | Phase 1 read-only |
| Evidence | health, reports, status, active-yaml-validation, day30-demo, phase1-closeout | usable | Phase 1 evidence |

## CLI Commands

| Command | Status | Notes |
|---------|--------|-------|
| alters-lab start | usable | Start server, --foreground, --no-open, --dry-run |
| alters-lab stop | usable | Stop server, --mode dev/packaged |
| alters-lab status | usable | Show status, --json |
| alters-lab doctor | usable | Health checks, actionable messages |
| alters-lab open | usable | Open browser, --no-start, --dry-run |
| alters-lab backup | usable | Backup data, --dry-run, --json, --include-logs/secrets |

## Data Records / Local Storage

> 20 record/config types across 12 P6 runtime areas + config/state. See `P11_M1_DATA_RECORD_INVENTORY.md` for full detail.

| Record Type | Storage Area | Create API | Read/List API | Frontend Access | Status |
|-------------|-------------|------------|---------------|-----------------|--------|
| Weekly Notes | weekly_notes | POST /obsidian-weekly-note/ingest | GET /obsidian-weekly-note/list | usable | usable |
| Weekly Reviews | weekly_reviews | POST /weekly-review/start | GET /weekly-review/list | usable | usable |
| Calibration Records | calibration_records | POST /action-alignment/score | GET /action-alignment/list | partial | partial |
| Self-Deception Challenges | self_deception_challenges | POST /self-deception-challenge/evaluate | GET /self-deception-challenge/list | missing | partial |
| Alter Recommendations | alter_recommendations | POST /alter-recommendation/recommend | GET /alter-recommendation/list | missing | partial |
| Weekly Reminders | reminders | POST /weekly-reminder/complete | GET /weekly-reminder/status | partial | partial |
| Pattern Reviews | pattern_reviews | POST /pattern-review/build | GET /pattern-review/list | missing | partial |
| Behavior Validation | behavior_validation | POST /behavior-validation/evaluate | GET /behavior-validation/report | missing | partial |
| Exports | exports | POST /p6-data-retention/export | GET /p6-data-retention/manifest | missing | partial |
| Provider Config | config_dir | POST /provider-config/config | GET /provider-config/config | usable | usable |
| Provider Secrets | config_dir | POST /provider-config/secret | GET /provider-config/status (redacted) | usable | usable |
| Generation Drafts | draft workspace | POST /generation-drafts/preview | GET /generation-drafts/list | missing | route_exists |
| Orchestration Plans | draft workspace | POST /promotion-orchestration/{id}/plan | GET /promotion-orchestration/list | missing | route_exists |
| Gate Reports | draft workspace | POST /promotion-execution-gate/{id}/check | GET /promotion-execution-gate/list | missing | route_exists |
| Live Execution Reports | draft workspace | POST /promotion-live-execution/{id}/run | GET /promotion-live-execution/list | missing | route_exists |
| Phase Closeout Reports | repo artifacts | phase*_closeout routers | phase*_closeout routers | missing | route_exists |
| Workflow Summaries | state_dir | POST /user-workflow/run-summary | GET /user-workflow/state | missing | route_exists |
| State (PID) | state_dir | local_launcher | local_launcher | missing | route_exists |
| Logs | state_dir | server log | (none) | missing | route_exists |

## Workflows

| Workflow | Status | Biggest Gap |
|----------|--------|-------------|
| Install package | usable | Verified by P9 lifecycle smoke |
| Launch app | usable | CLI start/open works |
| First run | usable | Getting Started page + checklist |
| Provider mock setup | usable | Default mock, no config needed |
| Weekly note ingest | usable | Full API + frontend flow |
| Weekly review | usable | 6-step flow end-to-end |
| Action alignment score | usable | Score submission works |
| Backup | usable | CLI backup with dry-run |
| Uninstall/remove | usable | Verified by P9 lifecycle smoke |
| Provider live setup | partial | Config works, but no real provider tested in production |
| P6 validation package | blocked_by_design | Intentionally blocked until app complete |

## Top Capability Gaps

1. **AlterDialogue**: Backend read-only, frontend exists but no real provider dialogue flow exercised
2. **CalibrationHistory**: No real calibration records to display (cold start)
3. **RubricDelta**: No real delta suggestions to display
4. **CheckpointPlan**: No real checkpoint plans to display
5. **RealityScore**: Score submission works but no real calibration loop exercised end-to-end
6. **Provider live setup**: Config/test works but no real provider integration tested in production
