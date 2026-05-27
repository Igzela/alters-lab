# P10 Taskbook

## Phase 10 — Personal Pilot & Real-Use Cutover

### P10-000: Personal Pilot & Real-Use Cutover Boundary Plan

**Status**: done
**Goal**: Define the next phase for moving Alters Lab from a sealed local product into Charlie's actual daily/weekly use.
**Depends on**: P9-M7 complete
**Notes**: Created P10 plan, taskbook, real-use boundary, P6 validation bridge, and pilot evidence requirements. Defined milestone table, excluded scope, hard boundaries, evidence policy, and friction policy.

### P10-M1: Local installation cutover checklist

**Status**: done
**Goal**: Create a checklist for cutting over from dev-mode to packaged app as the primary workflow. Verify packaged app works for real use.
**Depends on**: P10-000
**Notes**: Done. Created P10_M1_LOCAL_INSTALLATION_CUTOVER_CHECKLIST.md (9-section operator checklist covering build, install, verify packaged app, start/open, provider boundary, backup, personal data boundary, evidence capture) and P10_M1_CUTOVER_EVIDENCE_TEMPLATE.md (fillable redacted YAML template). Updated FIRST_RUN_CHECKLIST.md, INSTALL.md with cutover pointers. Updated 7 governance docs. No code changes. P6 remains NOT_VALIDATED/NOT_SEALED.

### P10-M2: First real weekly note ingest

**Status**: done
**Goal**: Charlie writes a real weekly note and ingests it into Alters Lab. First real-use evidence artifact.
**Depends on**: P10-M1
**Notes**: Done. Real weekly note ingested via packaged app API POST /obsidian-weekly-note/ingest. Record saved to local data dir. Evidence recorded in P10_M2_REAL_WEEKLY_NOTE_INGEST_EVIDENCE.md. P6 remains NOT_VALIDATED/NOT_SEALED.

### P10-M3: First real weekly review session

**Status**: done
**Goal**: Charlie runs a real weekly review session using Alters Lab. First real review cycle.
**Depends on**: P10-M2
**Notes**: Done. Real weekly review session completed via packaged app API. Action alignment score: 0.75 (aligned_progress). Evidence recorded in P10_M3_REAL_WEEKLY_REVIEW_EVIDENCE.md. P6 remains NOT_VALIDATED/NOT_SEALED.

### P10-M4: Real-use friction log and fix triage

**Status**: done
**Goal**: Capture product friction discovered during real use. Triage fixes vs deferred items.
**Depends on**: P10-M3
**Notes**: Done. Friction log created (P10_M4_REAL_USE_FRICTION_LOG.md) with 3 low-severity items, all accepted_no_fix. Fix triage created (P10_M4_FIX_TRIAGE.md) with 0 blocker friction. No fixes required before P6 validation start. P6 remains NOT_VALIDATED/NOT_SEALED.

### P10-M5: P6 validation start decision gate

**Status**: ready_with_approval
**Goal**: Explicit human/GPT decision on whether to start P6 4-week validation. Must not be automatic.
**Depends on**: P10-M4
**Notes**: Not started.

### P10-M6: Week 1 validation package

**Status**: blocked
**Goal**: If P6 validation is explicitly started, package Week 1 evidence. Only if Charlie explicitly authorizes P6 validation.
**Depends on**: P10-M5
**Notes**: Not started. Conditional on explicit P6 validation start.

### P10-M7: Pilot closeout / next phase decision

**Status**: blocked
**Goal**: Close out P10 pilot. Decide next phase: continue pilot, start P6 validation, or other work.
**Depends on**: P10-M6
**Notes**: Not started.
