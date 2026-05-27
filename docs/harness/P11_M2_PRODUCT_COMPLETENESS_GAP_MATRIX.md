# P11-M2: Product Completeness Gap Matrix

| gap_id | workflow | tier | gap_type | severity | blocks_normal_use | blocks_p6_reconsideration | recommended_phase | notes |
|--------|----------|------|----------|----------|-------------------|---------------------------|-------------------|-------|
| G-001 | weekly note ingest | 0 | none | none | false | false | keep | Works end-to-end. F-001 textarea sync is low severity, accepted. |
| G-002 | weekly review | 0 | none | none | false | false | keep | Works end-to-end. F-002 section validation is low severity, accepted. |
| G-003 | action alignment score | 0 | none | none | false | false | keep | Works end-to-end. |
| G-004 | install/launch/first-run | 0 | none | none | false | false | keep | All verified by P9 lifecycle smoke. |
| G-005 | provider disabled/mock | 0 | none | none | false | false | keep | ProviderSettings page full CRUD. |
| G-006 | backup | 0 | none | none | false | false | keep | CLI backup with dry-run verified. |
| G-007 | uninstall/remove | 0 | none | none | false | false | keep | Verified by P9 lifecycle smoke. |
| G-008 | reality score / calibration loop | 1 | frontend | medium | false | true | P11-M4 (plan) / P11-M5 (implement) | Form submits score. No calibration loop UI. No drift visualization. No history detail. Planning in M4, implementation in M5. |
| G-009 | pattern review | 1 | frontend | medium | false | true | P11-M4 (plan) / P11-M6 (implement) | Backend works (POST /build, GET /list). No frontend page. Planning in M4, implementation in M6. |
| G-010 | behavior validation | 1 | frontend | high | false | true | P11-M4 (plan) / P11-M6 (implement) | Backend works (POST /evaluate, GET /report). No frontend page. P6 validation depends on this. Planning in M4, implementation in M6. |
| G-011 | self-deception challenge | 1 | frontend | low | false | false | defer | Backend works. Supporting evidence for P6. No frontend. |
| G-012 | alter recommendation | 1 | frontend | low | false | false | defer | Backend works. Supporting evidence for P6. No frontend. |
| G-013 | P6 validation package | 1 | intentional_block | blocker | false | true | defer | Intentionally blocked until product complete. |
| G-014 | alter dialogue | 2 | e2e | low | false | false | defer | UI exists, backend works, but no persistent conversation history. Not needed for normal weekly use. |
| G-015 | CalibrationHistory | 2 | frontend | low | false | false | P11-M3 | List view works. Missing detail view and trend visualization. |
| G-016 | RubricDelta | 2 | data | low | false | false | defer | Cold start — API works but no real suggestions exist. |
| G-017 | CheckpointPlan | 2 | data | low | false | false | defer | Cold start — API works but no real plans exist. |
| G-018 | data export/delete/archive | 2 | frontend | low | false | false | defer | Backend works. No frontend page for data management. |
| G-019 | logs/doctor/troubleshooting | 2 | frontend | low | false | false | defer | CLI doctor works. No frontend log viewer. |
| G-020 | provider live setup | 3 | none | low | false | false | defer | Config/test works. No real provider tested. Defer until user enables. |

## Summary

- **Tier 0 gaps**: 0 (all core workflows work)
- **Tier 1 gaps**: 6 (5 frontend, 1 intentional_block; 3 P11-M4, 3 defer)
- **Tier 2 gaps**: 6 (3 frontend, 2 data, 1 e2e; 1 P11-M3, 5 defer)
- **Tier 3 gaps**: 1 (defer)

## Normal-Use Blockers

**None identified.** The core weekly review workflow works end-to-end.

## P6-Reconsideration Blockers

1. **G-010**: behavior validation frontend — high severity
2. **G-008**: reality score / calibration loop — medium severity
3. **G-009**: pattern review frontend — medium severity
4. **G-013**: P6 validation package — intentionally blocked
