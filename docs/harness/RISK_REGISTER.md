# Risk Register

## Active Risks

| ID | Risk | Likelihood | Impact | Mitigation | Status |
|----|------|------------|--------|------------|--------|
| R-001 | Real LLM integration prematurely | Medium | High | Quality gate enforcement; no API keys in codebase | Active |
| R-002 | Prediction distortion through hindsight bias | High | High | Blind prediction immutability; append-only retros | Active |
| R-003 | Privacy concerns with content data | Medium | Medium | Local-only storage; no external APIs in v0.1 | Active |
| R-004 | Scope creep beyond calibration system | Medium | High | Strict execution slice boundaries; human approval gates | Active |
| R-005 | Rubric over-fitting to small dataset | High | Medium | Require multi-retro evidence for rubric changes | Active |

## Risk Assessment

- **Likelihood**: Low / Medium / High
- **Impact**: Low / Medium / High
- **Status**: Active / Mitigated / Closed
