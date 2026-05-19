# Phase 3 Scope and Boundary Plan — Controlled Mutation

**Date:** 2026-05-19
**Status:** Sealed (P3-000)
**Predecessor:** Phase 2 Sealed Baseline (commit fcfcbe2)

---

## 1. Executive Summary

Phase 3 transitions the Alters System from a read-only runtime foundation to a controlled mutation environment. The read-only loader, validator, and API surface established in Phase 2 remain intact as the trust boundary. Phase 3 adds the ability for the backend to persist governed YAML artifacts through explicit API endpoints — replacing the manual file writes of Phase 1 with API-driven, auditable, rollback-capable mutation paths.

Every mutation in Phase 3 must pass through a governance gate. No write is automatic. No write is unreviewed. The boundary between read-only and write is explicit, tested, and enforced.

---

## 2. Phase 3 Objectives

### 2.1 Controlled Write Capabilities

Phase 3 introduces the following controlled write capabilities:

| Capability | Description | Trigger | Gate |
|------------|-------------|---------|------|
| Snapshot YAML Write | Persist confirmed in-memory snapshot as active YAML | POST endpoint + human confirmation | Governance approval |
| Branches YAML Write | Persist discovered branches as active YAML | POST endpoint + human confirmation | Governance approval |
| Alter YAML Write | Persist confirmed alter as active YAML | POST endpoint + human confirmation | Governance approval |
| Dialogue Runtime | Interactive dialogue with bounded provider | POST endpoint + session creation | Human approval + provider bounds |
| Calibration Scoring | Score branches against rubric dimensions | POST endpoint + confirmed inputs | Human approval + cold-start check |
| Drift Computation | Compare predicted vs. actual branch outcomes | POST endpoint + checkpoint data | Human approval |
| Archive Creation | Snapshot current state into timestamped archive | POST endpoint + cycle completion | Human review |

### 2.2 Modules Gaining Runtime Behavior

| Module | Phase 2 State | Phase 3 State |
|--------|---------------|---------------|
| Snapshot Intake | In-memory API + manual export | API-driven YAML persistence |
| Branch Discovery | Manual file write | API-driven YAML persistence |
| Alter Generation | Manual file write | API-driven YAML persistence |
| Dialogue Engine | Static YAML templates | Interactive provider-bounded sessions |
| Value Alignment | Manual file write | API-driven YAML persistence |
| Calibration | Static templates only | Scoring API with cold-start guard |
| Archive | Template folder only | Controlled archive creation |

### 2.3 What Remains Forbidden

| Forbidden | Rationale |
|-----------|-----------|
| LLM provider integration without bounds | Provider must be bounded (model, token limit, timeout); unbounded provider is forbidden |
| Database persistence | File-based governance remains; no SQL/NoSQL |
| Frontend | Backend-only; no web UI, no mobile |
| Autonomous generation without human approval | Every generation must pass through a human confirmation gate |
| Calibration scoring automation (cold-start) | Cold-start policy (first 3 checkpoints: record actuals only) still enforced |
| Archive creation without human review | Archive requires explicit human review before creation |
| Active YAML write without governance approval | Every write must pass approval gate |
| Rubric auto-modification | auto_modify: false is permanent |
| Provider token accumulation across sessions | Each session is bounded; no cross-session token state |

---

## 3. Allowed Writes

### 3.1 Snapshot YAML Write

- **Files modified:** `alters/current/snapshot.yaml`
- **Trigger:** POST `/snapshot-intake/sessions/{session_id}/persist` after confirm
- **Approval gate:** Human confirmation via confirm endpoint + governance check (snapshot has all 3 anchors, intake_status.phase is "completed")
- **Rollback plan:** Git revert to previous snapshot.yaml; backup copy created before write
- **Evidence:** Pre-write hash, post-write hash, confirmation timestamp, endpoint caller

### 3.2 Branches YAML Write

- **Files modified:** `alters/current/branches.yaml`
- **Trigger:** POST `/branches/persist` after branch discovery
- **Approval gate:** Human confirmation + governance check (3-4 branches, each with non-empty incompatible_with, structural differences verified)
- **Rollback plan:** Git revert to previous branches.yaml; backup copy created before write
- **Evidence:** Pre-write hash, post-write hash, branch count, confirmation timestamp

### 3.3 Alter YAML Write

- **Files modified:** `alters/current/alters/alter_{letter}.yaml`
- **Trigger:** POST `/alters/{branch_id}/persist` after alter generation
- **Approval gate:** Human confirmation + governance check (branch_ref exists, source_refs complete, voice non-neutral, tradeoffs non-empty)
- **Rollback plan:** Git revert; backup copy created before write
- **Evidence:** Pre-write hash, post-write hash, branch_ref, confirmation timestamp

### 3.4 Value Alignment YAML Write

- **Files modified:** `alters/current/value_alignment/alignment_{date}.yaml`
- **Trigger:** POST `/value-alignment/persist` after evaluation
- **Approval gate:** Human confirmation + governance check (all 5 dimensions assessed, requires_human_review is true, comparison matrix complete)
- **Rollback plan:** Git revert; backup copy created before write
- **Evidence:** Pre-write hash, post-write hash, dimension count, confirmation timestamp

### 3.5 Dialogue YAML Write

- **Files modified:** `alters/current/dialogue/dialogue_alter_{letter}_{date}.yaml`
- **Trigger:** POST `/dialogue/sessions` to create session, POST `/dialogue/sessions/{id}/messages` to add messages
- **Approval gate:** Human approval to start session + alter exists with valid branch_ref + full alter injection verified
- **Rollback plan:** Git revert; session can be abandoned (no partial writes)
- **Evidence:** Session ID, alter reference, message count, grounding metadata per response

### 3.6 Dialogue Runtime (Provider-Bounded)

- **Files modified:** Dialogue session YAML (see 3.5)
- **Trigger:** POST `/dialogue/sessions/{id}/messages` with user message
- **Approval gate:** Provider bounded (single model, token limit per response, timeout), human approval for session start, grounding metadata enforced
- **Rollback plan:** Session abandonment; provider errors halt session
- **Evidence:** Provider model, token usage per response, grounding metadata, error log

### 3.7 Calibration Scoring

- **Files modified:** `alters/calibration/scores/score_{date}.yaml`
- **Trigger:** POST `/calibration/score` with checkpoint data
- **Approval gate:** Human confirmation + cold-start guard (first 3 checkpoints: record actuals only, no drift computation)
- **Rollback plan:** Git revert; score file can be deleted
- **Evidence:** Checkpoint number, cold-start status, dimension scores, confirmation timestamp

### 3.8 Drift Computation

- **Files modified:** `alters/calibration/scores/score_{date}.yaml` (updated with drift data)
- **Trigger:** POST `/calibration/drift` with predicted and actual values
- **Approval gate:** Human confirmation + both predicted and actual values present + baseline established (checkpoint > 3)
- **Rollback plan:** Git revert; drift data can be removed from score file
- **Evidence:** Predicted values, actual values, drift magnitudes, confirmation timestamp

### 3.9 Archive Creation

- **Files modified:** `alters/archive/{date}_{cycle_id}/` (new folder with snapshot, branches, reality_trace, reality_score, resolution, rubric_delta, alters/)
- **Trigger:** POST `/archive/create` after cycle completion
- **Approval gate:** Human review + snapshot and branches exist + cycle is complete
- **Rollback plan:** Delete archive folder; active files unchanged
- **Evidence:** Archive folder path, file count, creation timestamp, human review record

---

## 4. Forbidden Writes (Must Remain Forbidden in Phase 3)

| Forbidden | Why |
|-----------|-----|
| **LLM provider integration without bounds** | Provider must be bounded: single model, token limit, timeout, no cross-session state. Unbounded provider risks uncontrolled generation. |
| **Database persistence** | File-based governance is the trust model. Database introduces durability guarantees that conflict with YAML-as-source-of-truth. |
| **Frontend** | Backend-only system. No web UI, no mobile, no desktop app. All interaction through API endpoints. |
| **Autonomous generation without human approval** | Every alter, dialogue session, calibration score, and archive requires explicit human confirmation. No auto-generation. |
| **Calibration scoring automation** | Cold-start policy enforced: first 3 checkpoints record actuals only. No drift computation without baseline. Scoring requires human confirmation. |
| **Archive creation without human review** | Archive requires explicit human review before creation. No automatic archiving on cycle completion. |
| **Active YAML write without governance approval** | Every write to alters/current/ must pass through governance check. No bypass. |
| **Rubric auto-modification** | auto_modify: false is permanent. Rubric changes require documented human decision + decision record. |
| **Provider token accumulation across sessions** | Each dialogue session is bounded. No cross-session token state. Session ends → tokens reset. |
| **Write to alters/calibration/rubric.yaml without human decision** | Rubric changes are proposal-only (reject_auto_apply: true). Only human decision can modify rubric. |

---

## 5. Approval Gates

### 5.1 Governance Checks (Automated)

| Gate | Check | Enforced By |
|------|-------|-------------|
| Snapshot completeness | All 3 anchors present, intake_status.phase == "completed" | API endpoint validation |
| Branch structural incompatibility | 3-4 branches, non-empty incompatible_with, structural differences | API endpoint validation |
| Alter branch reference | branch_ref points to existing branch, source_refs complete | API endpoint validation |
| Value alignment completeness | All 5 dimensions assessed, requires_human_review == true | API endpoint validation |
| Dialogue full inject | Complete alter.yaml injected, grounding metadata present | API endpoint validation |
| Cold-start guard | Checkpoint count checked before drift computation | API endpoint validation |
| Rubric auto_modify | Always false; checked before any rubric write | API endpoint validation |

### 5.2 Human Approval Required

| Operation | Approval Required |
|-----------|-------------------|
| Snapshot persist | Human confirms snapshot via `/snapshot-intake/sessions/{id}/confirm` |
| Branches persist | Human confirms branches via `/branches/confirm` |
| Alter persist | Human confirms alter via `/alters/{branch_id}/confirm` |
| Value alignment persist | Human confirms alignment via `/value-alignment/confirm` |
| Dialogue session start | Human approves session via `/dialogue/sessions` |
| Calibration scoring | Human confirms checkpoint data via `/calibration/score` |
| Drift computation | Human confirms predicted vs. actual via `/calibration/drift` |
| Archive creation | Human reviews and approves via `/archive/create` |
| Rubric modification | Human documents decision in DECISION_RECORD.md |

### 5.3 Evidence Recorded

For every write operation:
- Pre-write hash of target file (if exists)
- Post-write hash of target file
- Confirmation timestamp
- Endpoint caller (API vs. manual)
- Governance check result (PASS/FAIL with details)
- Human approval record (session ID, confirmation token)

---

## 6. Rollback / Recovery Plan

### 6.1 Per-Write Rollback

| Write Type | Rollback Method | Recovery Time |
|------------|-----------------|---------------|
| Snapshot YAML | `git checkout HEAD~1 -- alters/current/snapshot.yaml` | < 1 minute |
| Branches YAML | `git checkout HEAD~1 -- alters/current/branches.yaml` | < 1 minute |
| Alter YAML | `git checkout HEAD~1 -- alters/current/alters/alter_*.yaml` | < 1 minute |
| Value Alignment YAML | `git checkout HEAD~1 -- alters/current/value_alignment/alignment_*.yaml` | < 1 minute |
| Dialogue YAML | `git checkout HEAD~1 -- alters/current/dialogue/dialogue_*.yaml` | < 1 minute |
| Calibration Score | `git checkout HEAD~1 -- alters/calibration/scores/score_*.yaml` | < 1 minute |
| Archive Folder | `rm -rf alters/archive/{date}_{cycle_id}/` | < 1 minute |

### 6.2 Backup Strategy

Before every write:
1. If target file exists: compute SHA-256 hash, store in write audit log
2. If target file exists: create `.bak` copy in same directory
3. After write: compute new SHA-256 hash, verify write succeeded
4. On rollback: restore from `.bak` or git revert

### 6.3 Successful Rollback Criteria

- Target file matches pre-write hash (or is deleted if file was new)
- No cascading writes (rolling back snapshot does not auto-rollback branches)
- Audit log records the rollback with reason
- Tests pass after rollback

---

## 7. Evidence Requirements

### 7.1 Per-Write Evidence

| Field | Description |
|-------|-------------|
| `operation` | Write type (snapshot_persist, branches_persist, etc.) |
| `timestamp` | ISO 8601 timestamp of write |
| `pre_write_hash` | SHA-256 of target file before write (null if new file) |
| `post_write_hash` | SHA-256 of target file after write |
| `target_path` | Absolute path to target file |
| `endpoint` | API endpoint that triggered the write |
| `governance_check` | PASS/FAIL with specific checks passed |
| `human_approval` | Confirmation token or session ID |
| `rollback_available` | true if backup exists |

### 7.2 Evidence Storage

- Write audit log: `docs/harness/phase3_write_audit.jsonl` (one JSON line per write)
- Pre-write backups: `.bak` files in same directory as target
- Git history: every write is a commit

### 7.3 Evidence Auditing

- Phase 3 closeout verifies all writes have matching pre/post hashes
- Git log shows all writes as commits
- `.bak` files can be diffed against current files
- Audit log can be parsed for governance_check == FAIL (should be empty)

---

## 8. Final Gate Criteria for Phase 3

### 8.1 What Must Be True

| Criterion | Verification |
|-----------|-------------|
| All Phase 3 slices committed | Git log shows P3-001 through P3-XXX |
| All tests passing | pytest suite passes with 0 failures |
| No forbidden components | Boundary checks confirm no provider without bounds, no database, no frontend |
| No ungoverned writes | Audit log shows every write has governance_check == PASS |
| No rubric auto-modification | auto_modify remains false, no rubric writes without decision record |
| No cold-start violations | No drift computation before checkpoint > 3 |
| Active YAML chain valid | validate_active_yaml_chain returns PASS |
| Rollback tested | At least one rollback per write type demonstrated in tests |

### 8.2 Tests Must Pass

| Test Category | Count Target |
|---------------|-------------|
| Existing Phase 1 + Phase 2 tests | 118 (no regressions) |
| Phase 3 snapshot write tests | 10+ |
| Phase 3 branches write tests | 10+ |
| Phase 3 alter write tests | 10+ |
| Phase 3 dialogue runtime tests | 15+ |
| Phase 3 calibration tests | 10+ |
| Phase 3 drift tests | 10+ |
| Phase 3 archive tests | 10+ |
| Phase 3 boundary/governance tests | 15+ |
| **Total target** | **~200+** |

### 8.3 Boundaries Must Hold

| Boundary | Enforcement |
|----------|-------------|
| No unbounded provider | Provider config validated per session |
| No database | Import checks (no sqlalchemy, no database drivers) |
| No frontend | No apps/web, no React/Vue/Svelte imports |
| No autonomous generation | Every generation requires human confirmation token |
| No rubric auto-modify | auto_modify field checked in all rubric write paths |
| No cold-start drift | Checkpoint count checked before drift computation |
| No ungoverned YAML write | Every write passes governance gate |
| Read-only routes untouched | cycle-summary and evidence routers remain GET-only |

---

## 9. Execution Slice Map (P3-001 through P3-007)

### Slice Dependency Graph

```
P3-000 (Scope Plan) ← YOU ARE HERE
  ├─→ P3-001 (Snapshot Write API)
  │     └─→ P3-002 (Branches Write API)
  │           └─→ P3-003 (Alter Write API)
  │                 ├─→ P3-004 (Dialogue Runtime)
  │                 └─→ P3-005 (Value Alignment Write API)
  │                       └─→ P3-006 (Calibration + Drift API)
  │                             └─→ P3-007 (Archive + Closeout)
```

### Slice Details

| Slice | Title | Complexity | Dependencies | Description |
|-------|-------|------------|--------------|-------------|
| P3-000 | Phase 3 Scope and Boundary Plan | Low | P2-005R | Define boundaries before implementation |
| P3-001 | Controlled Snapshot Write API | Medium | P3-000 | POST endpoint to persist confirmed snapshot; backup + audit + rollback |
| P3-002 | Controlled Branches Write API | Medium | P3-001 | POST endpoint to persist discovered branches; governance check for structural incompatibility |
| P3-003 | Controlled Alter Write API | Medium | P3-002 | POST endpoint to persist confirmed alter; governance check for branch_ref, voice, tradeoffs |
| P3-004 | Dialogue Runtime (Provider-Bounded) | High | P3-003 | Interactive dialogue with bounded provider; grounding metadata; session management |
| P3-005 | Value Alignment Write API | Medium | P3-003 | POST endpoint to persist alignment; governance check for 5 dimensions, requires_human_review |
| P3-006 | Calibration + Drift API | High | P3-005 | Scoring with cold-start guard; drift computation; rubric integrity checks |
| P3-007 | Archive + Phase 3 Closeout | Medium | P3-006 | Controlled archive creation; phase 3 closeout report; seal baseline |

### Estimated Total Effort

- P3-001: 1 slice
- P3-002: 1 slice
- P3-003: 1 slice
- P3-004: 1-2 slices (provider integration complexity)
- P3-005: 1 slice
- P3-006: 1-2 slices (cold-start + drift logic)
- P3-007: 1 slice
- **Total: 7-9 slices**

---

## 10. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Mitigation |
|----|------|------------|--------|------------|
| R-029 | Provider integration introduces unbounded generation | Medium | High | Provider bounded per session: single model, token limit, timeout. Grounding metadata enforced. Tests verify bounds. |
| R-030 | API-driven writes bypass governance gates | Low | High | Every write endpoint calls governance check function. Tests verify governance check is called. Audit log records gate result. |
| R-031 | Rollback fails silently (file restored but state inconsistent) | Low | High | Rollback tests verify post-rollback hash matches pre-write hash. Active YAML chain validated after rollback. |
| R-032 | Cold-start policy violated (drift before baseline) | Medium | High | Checkpoint count guard in drift endpoint. Tests verify 403 response when checkpoint <= 3. |
| R-033 | Dialogue session accumulates unbounded context | Medium | Medium | Token limit per response. Session timeout. No cross-session state. Tests verify token limits. |
| R-034 | Archive creation mutates active files | Low | High | Archive writes only to archive/ folder. Tests verify active files unchanged after archive creation. |
| R-035 | Audit log grows unbounded | Low | Low | Audit log is JSONL, append-only. Can be rotated. No impact on system operation. |
| R-036 | Phase 3 slices introduce forbidden components | Medium | High | Boundary tests run on every slice. Import checks for provider, database, frontend. Same pattern as Phase 2. |
| R-037 | Existing Phase 1/2 tests break from Phase 3 changes | Medium | High | Phase 3 slices extend, not modify, existing code. Regression test run after each slice. No breaking changes to existing endpoints. |
| R-038 | Governance gate becomes a bottleneck | Medium | Medium | Gates are automated (API validation), not manual queues. Human approval is confirm/dismiss, not review queues. |

---

## Appendix: Phase Transition Summary

| Phase | Read Capability | Write Capability | Runtime |
|-------|----------------|------------------|---------|
| Phase 0 | Manual file read | Manual file write | None |
| Phase 1 | Manual file read | Controlled YAML write (manual) | In-memory API (snapshot intake only) |
| Phase 2 | Read-only loader + API | None (forbidden) | Read-only API endpoints |
| **Phase 3** | Read-only loader + API | **Controlled YAML write (API-driven)** | **Bounded provider dialogue, calibration, drift** |
