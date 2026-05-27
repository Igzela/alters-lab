# P11-M2: Missing Core Workflow Map

## Workflow Tier Classification

### Tier 0 — Must work for normal weekly use

| # | Workflow | Status | Frontend | Backend | Data Records | Normal-Use Impact | Recommendation |
|---|----------|--------|----------|---------|--------------|-------------------|----------------|
| 1 | Install package | usable | N/A | N/A | config.yaml | none | keep |
| 2 | Launch app | usable | auto-opens browser | GET /health | PID file | none | keep |
| 3 | First run | usable | GettingStarted page (static) | GET /product/status | config.yaml created | none | keep |
| 4 | Provider disabled | usable | ProviderSettings shows "disabled" | GET /provider-config/status | config.yaml | none | keep |
| 5 | Provider mock setup | usable | ProviderSettings full CRUD | POST /provider-config/* | config.yaml, secrets.yaml | none | keep |
| 6 | Weekly note ingest | usable | WeeklyReview Step 1 | POST /obsidian-weekly-note/ingest | weekly_notes/*.yaml | none | keep |
| 7 | Weekly review | usable | WeeklyReview Steps 2-5 | POST /weekly-review/* | weekly_reviews/*.yaml | none | keep |
| 8 | Action alignment score | usable | WeeklyReview Step 5 | POST /action-alignment/score | calibration_records/*.yaml | none | keep |
| 9 | Backup | usable | N/A (CLI only) | CLI backup | exports/*.tar.gz | none | keep |
| 10 | Uninstall/remove | usable | N/A (system package) | N/A | preserves user data | none | keep |

### Tier 1 — Needed for P6 validation readiness

| # | Workflow | Status | Frontend | Backend | Data Records | P6-Readiness Impact | Recommendation |
|---|----------|--------|----------|---------|--------------|---------------------|----------------|
| 11 | Reality score / calibration loop | partial | RealityScore form (submit only) | POST /calibration-loop/reality-scores, drift/calculate | calibration_records/*.yaml | medium — P6 needs demonstrated calibration | frontend_gap |
| 12 | Pattern review | partial | missing frontend | POST /pattern-review/build, GET /list | pattern_reviews/*.yaml | medium — P6 needs 4-week pattern evidence | frontend_gap |
| 13 | Behavior validation | partial | missing frontend | POST /behavior-validation/evaluate, GET /report | behavior_validation/*.yaml | high — P6 validation gate depends on this | frontend_gap |
| 14 | Self-deception challenge | partial | missing frontend | POST /self-deception-challenge/evaluate, GET /list | self_deception_challenges/*.yaml | low — supporting evidence for P6 | defer |
| 15 | Alter recommendation | partial | missing frontend | POST /alter-recommendation/recommend, GET /list | alter_recommendations/*.yaml | low — supporting evidence for P6 | defer |
| 16 | P6 validation package | blocked_by_design | N/A | /behavior-validation/*, /p6-data-retention/* | N/A | blocker — intentionally blocked | defer |

### Tier 2 — Useful product completeness

| # | Workflow | Status | Frontend | Backend | Data Records | Normal-Use Impact | Recommendation |
|---|----------|--------|----------|---------|--------------|-------------------|----------------|
| 17 | Alter dialogue | partial | AlterDialogue page (UI exists) | POST /provider-dialogue/{alter_id}/reply | no new records | low — nice-to-have for normal use | e2e_gap |
| 18 | CalibrationHistory | partial | CalibrationHistory page (list only) | GET /calibration-loop/history | reads calibration_records | low — visibility into calibration | frontend_gap |
| 19 | RubricDelta | partial | RubricDelta page (cold start) | POST /rubric-delta/suggest | rubric delta area | low — useful but not blocking | defer |
| 20 | CheckpointPlan | partial | CheckpointPlan page (cold start) | POST /checkpoint-regeneration/plan | checkpoint area | low — useful but not blocking | defer |
| 21 | Data export/delete/archive | partial | missing frontend | POST /p6-data-retention/* | exports/*.yaml | low — data management visibility | frontend_gap |
| 22 | Logs/doctor/troubleshooting | partial | missing frontend | CLI doctor, GET /local-app/status | logs/ | low — diagnostic visibility | defer |

### Tier 3 — Optional / deferred

| # | Workflow | Status | Frontend | Backend | Data Records | Notes |
|---|----------|--------|----------|---------|--------------|-------|
| 23 | Provider live setup | partial | ProviderSettings | POST /provider-config/*, POST /provider-connectivity/check | config.yaml, secrets.yaml | Config works but no real provider tested. Defer until user explicitly enables. |

---

## Core Missing Workflows for Normal Use

The app currently works for the **core weekly review loop**: ingest → review → score. This is the essential daily-use workflow and it functions end-to-end.

**What's missing for "normally usable" app:**

1. **CalibrationHistory detail view** — Users can see a list of calibration records but cannot drill into individual records or see trends over time. Impact: low (list view works).

2. **Pattern review frontend** — Backend works, but no way for users to see 4-week patterns without using the API directly. Impact: low (pattern review is periodic, not weekly).

3. **Behavior validation frontend** — Backend works, but no UI to view validation reports. Impact: low for normal use, medium for P6 readiness.

**What's NOT missing for normal use:**

- The core weekly review flow (ingest → start → complete → score) works end-to-end
- Provider setup/testing works end-to-end
- Backup works via CLI
- First-run onboarding works
- Install/uninstall works

---

## Normal-Use Blockers

**None.** The core weekly review workflow (the primary normal-use workflow) is functional. All identified gaps are in secondary or visibility features that do not block normal weekly use.

---

## P6-Readiness Blockers

1. **Behavior validation frontend** (high) — P6 validation needs demonstrated behavior validation. Backend exists but no frontend visibility.
2. **Pattern review frontend** (medium) — P6 validation benefits from 4-week pattern evidence. Backend exists but no frontend.
3. **Reality score / calibration loop e2e** (medium) — Score submission works but no end-to-end calibration loop exercised.
4. **P6 validation package** (blocker by design) — Intentionally blocked until product is complete.
