# Risk Register

## Active Risks

| ID | Risk | Likelihood | Impact | Mitigation | Status |
|----|------|------------|--------|------------|--------|
| R-001 | Scope drift beyond Alters System | Medium | High | Strict execution slice boundaries; alters-system-design.md as source of truth; human approval gates | Active |
| R-002 | LLM hallucinated Alter (when LLM integration added) | High | High | Phase 0 has no LLM; when added, require human review of all generated Alters before use | Active |
| R-003 | Branch defined as result difference instead of structural difference | High | Medium | Quality gate: structural_difference must describe kind, not degree; branches must be mutually incompatible | Active |
| R-004 | Rubric auto-modification | Medium | High | auto_modify field always false; all rubric changes require documented human decision | Active |
| R-005 | Private data leakage through Alter or Snapshot files | Medium | Medium | File-based local storage only; no external APIs in v0.1; no LLM provider calls | Active |
| R-006 | Over-engineering before Phase 0 is validated | High | High | Phase 0 is file-based only; no application code until Phase 0 workflow is validated by human | Active |
| R-007 | Accidental return to content-calibration domain | Low | High | P1-001 explicitly forbids content-calibration code; all work framed as future-branch simulation | Active |
| R-008 | Premature full-stack implementation | Medium | High | P1-001 is backend-only; no frontend, no database, no LLM provider in this slice | Active |
| R-009 | Branch/alter generation before snapshot validation | Medium | High | Snapshot contract and validation rules are stable before any branch/alter code is written | Active |
| R-010 | Provider/LLM integration before local contracts are stable | Medium | High | P1-001 has zero provider code; no external API calls; contracts validated locally first | Active |
| R-011 | Mutating confirmed YAML without human approval | Medium | High | Active YAML files are forbidden territory in P1-001; only schemas and pure functions | Active |
| R-012 | In-memory API mistaken for durable persistence | Medium | Medium | P1-002 explicitly uses in-memory store; README and docs state this is not durable; data lost on restart is expected | Active |
| R-013 | Accidental active YAML mutation through API | Low | High | API performs zero file writes; confirm endpoint returns snapshot in-memory only; tests verify no YAML written | Active |
| R-014 | Out-of-order intake answers corrupting snapshot | Low | High | API enforces one-question-at-a-time order; rejects out-of-order and duplicate answers with 409 | Active |
| R-015 | Premature Branch Discovery trigger from API confirmation | Low | High | confirm endpoint does not trigger Branch Discovery; ready_for_branch_discovery is a flag only | Active |
| R-016 | Frontend or provider work starting before backend contract is stable | Medium | High | P1-002 forbids frontend and provider code; contract validated through 33 tests before any client integration | Active |
| R-017 | Export functions accidentally called from confirm endpoint | Low | High | P1-003 export is service-only; confirm endpoint does not import or call snapshot_export; tests verify confirm remains in-memory | Active |
| R-018 | write_snapshot_yaml writing to alters/current/snapshot.yaml by default | Low | High | write_snapshot_yaml requires explicit target_path; no hardcoded paths; tests use tmp_path only | Active |
| R-019 | Schema drift between Phase 0 templates and Phase 1 active artifacts | Medium | High | Phase 0 templates remain inactive_template_only; Phase 1 uses flat active schema with source_refs/quality_status; governance docs updated to reflect both; DECISION_RECORD.md P1-010-01 documents the divergence | Active |
| R-020 | Governance docs lagging behind active implementation | Medium | Medium | This governance docs update (P1-011 blocker) aligns PROJECT_BOARD, TASK_QUEUE, QUALITY_GATES, DECISION_RECORD, and RISK_REGISTER with P1-004 through P1-010 completion; periodic governance review recommended | Active |
| R-021 | Quality gates contradicting current phase artifacts | Medium | High | QUALITY_GATES.md updated to accept active alignment files after human confirmation and flat active Alter schema with source_refs/quality_status; gates now match Phase 1 reality | Active |
| R-022 | Governance docs overstating runtime capability | Medium | Medium | Titles corrected to "Controlled YAML Write" for P1-004 through P1-009; decision record documents the clarification; periodic review recommended | Active |
| R-023 | Static YAML writes confused with backend automation | Medium | Medium | P1-004 through P1-009 are file-based artifact generation, not running services; QUALITY_GATES updated to reflect actual scope; integration (P1-011) will clarify runtime vs. static boundary | Active |

## Risk Assessment

- **Likelihood**: Low / Medium / High
- **Impact**: Low / Medium / High
- **Status**: Active / Mitigated / Closed
