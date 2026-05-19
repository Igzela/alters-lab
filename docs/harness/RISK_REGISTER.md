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

## Risk Assessment

- **Likelihood**: Low / Medium / High
- **Impact**: Low / Medium / High
- **Status**: Active / Mitigated / Closed
