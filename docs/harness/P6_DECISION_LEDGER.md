# P6 Decision Ledger

**Phase**: P6 — Personal Long-Term Use Hardening
**Created**: 2026-05-20
**Source**: P6-000 grill session decisions

## Ledger Entries

### P6-DL-01: Personal Long-Term Use Over Public Productization

**Date**: 2026-05-20
**Decision**: P6 is defined as personal long-term use hardening, not public productization.
**Rationale**: The system has not been validated by real usage. Public productization without personal validation would build on unproven foundations.
**Consequence**: P6 scope focuses on Charlie's actual usage patterns, not market features.

### P6-DL-02: Behavior Change as Success Standard

**Date**: 2026-05-20
**Decision**: P6 success is measured by behavior change, not feature completion.
**Rationale**: Code completion without behavior change is productivity theatre.
**Consequence**: P6 requires 4-week validation window with measurable behavior change before sealing.

### P6-DL-03: Obsidian Raw Note as Primary Evidence

**Date**: 2026-05-20
**Decision**: Obsidian raw weekly note is the primary evidence source. System cannot invent weekly facts.
**Rationale**: User-written notes are more honest than system-generated summaries.
**Consequence**: System extracts structure from raw notes but cannot fabricate facts.

### P6-DL-04: Action Alignment as Primary Metric

**Date**: 2026-05-20
**Decision**: `action_alignment` is the primary metric — whether actions match the user's endorsed direction.
**Rationale**: Direction without execution is noise; execution without direction is drift.
**Consequence**: All scoring and review centers on alignment between stated direction and actual action.

### P6-DL-05: Dual-Layer Output

**Date**: 2026-05-20
**Decision**: P6 produces two-layer output: human-readable `review_note` and machine-readable `calibration_record`.
**Rationale**: Human review needs narrative; system tracking needs structure.
**Consequence**: Both layers must be produced per session; neither is optional.

### P6-DL-06: 4-Week Validation Window

**Date**: 2026-05-20
**Decision**: P6 requires 4 weeks of real use before sealing.
**Rationale**: One week is noise; four weeks shows patterns.
**Consequence**: P6_CODE_COMPLETE is not sufficient. P6_BEHAVIOR_VALIDATED requires 4 weekly reviews, 4 calibration records, 1 monthly pattern review, and measurable change.

### P6-DL-07: Provider Default Disabled/Mock

**Date**: 2026-05-20
**Decision**: Provider remains disabled or mock by default. Real provider requires explicit user configuration.
**Rationale**: Weekly review must work without external dependencies. Provider output must not be mistaken for truth.
**Consequence**: No API key committed. No default real provider calls. Real provider output cannot auto-write active YAML.

### P6-DL-08: No-Improvement Requires Usage Integrity Audit First

**Date**: 2026-05-20
**Decision**: If no behavior improvement after 4 weeks, first audit usage integrity before adding features or redesigning.
**Rationale**: No improvement may mean the system was not used honestly, not that the system is wrong.
**Consequence**: Usage integrity checks: weekly notes completed honestly, calibration records created, primary corrections set, failure reviews honest, self_deception_risk not softened, sessions not skipped too often. If usage invalid, fix usage behavior. If usage valid but no improvement, decide redesign or stop expansion.
