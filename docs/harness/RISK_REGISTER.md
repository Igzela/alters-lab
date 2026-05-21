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
| R-024 | Loader accidentally mutates active YAML | Low | High | Loader uses yaml.safe_load only; tests verify hash/text of snapshot.yaml, branches.yaml, reality_trace.yaml unchanged after load+validate+summarize | Active |
| R-025 | Loader becomes hidden generation runtime | Low | High | Loader package is read-only by design; no write functions; no branch/alter/dialogue/value/calibration/archive generation; boundary tests verify no forbidden routers added | Active |
| R-026 | Validators drift from Quality Gates | Medium | Medium | validate_active_yaml_chain validates against sealed baseline schema; changes to Quality Gates require matching validator updates | Active |
| R-027 | Phase 1 sealed baseline overwritten by Phase 2 | Low | High | Phase 2 loader is read-only; no YAML mutation; no archive creation; git diff verifies no changes to alters/current, alters/calibration, alters/archive | Active |
| R-028 | Future runtime built before read-only validation is stable | Medium | High | P2-001 establishes read-only loader + validation as prerequisite; P2-002 CLI tool depends on stable loader; no generation runtime until read-only layer is proven | Active |
| R-029 | Magic approval token mistaken for auth | Medium | High | P3-001R2 removed magic token; any non-empty token accepted as evidence; raw token never stored or logged | Mitigated |
| R-030 | Token hash accepted without human process | Low | Medium | Governance checks enforce completed snapshot + human_provided source_mode before any write; audit trail records caller | Active |
| R-031 | Dry-run response leaking full YAML | Low | Medium | P3-001R2 dry_run returns hashes/target/governance only; no full YAML in response; tested | Mitigated |
| R-032 | Hardcoded active path causing test mutation | Medium | High | P3-001R2 uses monkeypatchable path helpers; tests use tmp_path; real active YAML verified unchanged | Mitigated |
| R-033 | Audit record overexposing operational details | Low | Medium | P3-001R2 audit includes operation/timestamp/target/hashes/token_hash/caller/governance/backup; no raw token | Mitigated |
| R-034 | Stale audit evidence mistaken for approved write | Medium | High | P3-001R3 removed old-schema audit entries; audit logs only committed for real approved persist operations | Mitigated |
| R-035 | Old-schema audit logs mixed with new schema | Low | Medium | P3-001R3 removed all old-schema entries; new schema uses operation/pre_write_hash/post_write_hash/governance_check | Mitigated |
| R-036 | Test-generated audit logs committed as governance evidence | Medium | High | P3-001R3 policy: only committed for explicitly approved real persist; tests use monkeypatched paths | Mitigated |
| R-037 | Active YAML write traces left after rollback | Low | Medium | write_snapshot_with_audit creates backup before write; rollback_available flag in audit; backup under configurable dir | Active |
| R-038 | Forbidden fields silently ignored by Pydantic before service validation | Medium | High | P3-M1R: all branches/alters schemas use ConfigDict(extra="forbid"); smuggled fields rejected at 422; tested at API and schema level | Mitigated |
| R-039 | Batch alter persist not fully transactional on filesystem failure | Low | Medium | All alters validated before any write; filesystem failure midway leaves partial writes; future hardening may add temp-file atomic writes or rollback-on-error | Active |
| R-040 | Draft output mistaken for active state | Medium | High | Drafts explicitly marked draft_only, active_write_allowed=false, human_review_required=true; active promotion requires separate controlled persist APIs | Mitigated |
| R-041 | Deterministic templates overtrusted as intelligence | Medium | Medium | Templates produce candidate artifacts only; all drafts require human review; no claim of finality | Active |
| R-042 | Provider integration added too early | Medium | High | P3-M2 uses no provider imports; tests grep for provider imports; provider integration deferred to explicit later phase | Mitigated |
| R-043 | Draft audit logs committed as governance evidence | Low | Medium | Draft audit logs gitignored; only committed for explicitly approved real persist operations | Mitigated |
| R-044 | Mocked loader shape hiding production failure | Medium | High | P3-M2R added normalize_active_chain to handle ActiveYamlChain dataclass and dict; real loader smoke test proves API works without monkeypatching | Mitigated |
| R-045 | Wrapped YAML document shape mismatch | Medium | High | P3-M2R added extract_snapshot_body to handle {"snapshot": {...}} and unwrapped shapes; tests cover both | Mitigated |
| R-046 | Generation drafts built from invalid active chain | Low | High | P3-M2R API validates inputs before generation; validation failure returns 400, no draft/audit written | Mitigated |
| R-047 | Promotion package mistaken for active state | Medium | High | P3-M3 decision: promotion package is review artifact, not active state; active_write_allowed=false; requires_controlled_persist_api=true | Mitigated |
| R-048 | Review endpoint accidentally calling persist APIs | Low | High | P3-M3 service has no imports from branches_persist/alters_persist; grep check confirms no persist API calls | Mitigated |
| R-049 | Path traversal via draft_id | Low | High | load_draft_package rejects draft_id containing /, \\, or .. | Mitigated |
| R-050 | Raw approval token stored in review artifacts | Low | Medium | save_review_decision and save_promotion_package reject blank tokens; yaml.dump of model_dump excludes raw token | Mitigated |
| R-051 | Orchestration plan mistaken for execution | Medium | High | P3-M4: plan is not execution; execution_allowed_in_p3_m4=false; human final approval required; plan-only mode documented | Mitigated |
| R-052 | Plan endpoint accidentally calling persist APIs | Low | High | P3-M4 service has no imports from branches_persist/alters_persist; grep check confirms no persist API calls | Mitigated |
| R-053 | Invalid promotion package producing unsafe execution plan | Medium | High | P3-M4 validate_promotion_package_for_orchestration rejects invalid packages; plan cannot be built from invalid package | Mitigated |
| R-054 | Missing rollback/evidence requirements before active promotion | Low | High | P3-M4 build_evidence_requirements and build_rollback_plan produce mandatory requirements; plan includes evidence and rollback | Mitigated |
| R-055 | Path traversal via draft_id in orchestration | Low | High | validate_draft_id rejects /, \\, .., empty string | Mitigated |
| R-056 | Raw approval token stored in orchestration plan | Low | Medium | save_orchestration_plan rejects blank tokens; yaml.dump of model_dump excludes raw token; hash stored only | Mitigated |
| R-057 | Execution gate mistaken for live execution | Medium | High | P3-M5: gate is not execution; execution_allowed_now=false; live_execution_allowed_in_p3_m5=false; requires_p3_m6_live_execution=true | Mitigated |
| R-058 | Gate endpoint accidentally calling persist APIs | Low | High | P3-M5 service has no imports from branches_persist/alters_persist; grep check confirms no persist API calls | Mitigated |
| R-059 | Invalid promotion package producing unsafe gate report | Medium | High | P3-M5 validate_promotion_package_for_execution_gate rejects invalid packages; gate cannot pass with invalid package | Mitigated |
| R-060 | Missing prerequisites before live execution | Low | High | P3-M5 build_prerequisite_checks produces mandatory checks; gate cannot pass without all blocking prerequisites | Mitigated |
| R-061 | Path traversal via draft_id in execution gate | Low | High | validate_draft_id rejects /, \\, .., empty string | Mitigated |
| R-062 | Raw approval token stored in execution gate report | Low | Medium | save_gate_report rejects blank tokens; yaml.dump of model_dump excludes raw token; hash stored only | Mitigated |
| R-063 | Stale closeout evidence causing false Phase 3 seal | Medium | High | P3-M8R2: closeout evidence now uses git ls-files to distinguish tracked vs untracked audit files; PASS_WITH_NOTES for ignored runtime artifacts | Mitigated |
| R-064 | Raw audit file misclassified due to filesystem-only check | Medium | High | P3-M8R2: replaced filesystem glob with git ls-files tracking check; FAIL only for tracked files, WARN for local untracked | Mitigated |
| R-065 | Phase 4 scope creep into broad frontend/product | Medium | High | P4-000: scope explicitly limits frontend to dialogue, reality score form, calibration history; broad product UI excluded | Active |
| R-066 | LLM output promoted without pending_review | Medium | High | P4-000: promotion model requires schema validation → quality gate → pending_review → explicit human confirmation | Active |
| R-067 | Dialogue output mistaken for persistent user truth | Low | Medium | P4-000: dialogue is read-only by default; dialogue output must not write active YAML; saved session logs are evidence only | Active |
| R-068 | Drift score triggering automatic regeneration | Low | High | P4-000: drift is evidence only; no automatic regeneration; checkpoint regeneration requires drift > 0.6 threshold AND explicit trigger | Active |
| R-069 | Rubric suggestion auto-written without confirmation | Low | High | P4-000: rubric_delta_suggestion is suggestion only; rubric cannot be auto-written; requires explicit human action | Active |
| R-070 | Dialogue output mistaken for active truth | Low | Medium | P4-M1: dialogue is read-only; prompt packets include persistence_policy=read_only_no_active_yaml_write; no active YAML write capability | Mitigated |
| R-071 | Provider accidentally called from dialogue runtime | Low | High | P4-M1: provider_ready=false enforced; no provider imports in alter_dialogue service/API; grep check confirms no provider patterns | Mitigated |
| R-072 | Alter persona drift from active YAML | Low | Medium | P4-M1: validate_active_alter_for_dialogue checks voice.core_stance, branch_ref, source_refs, quality_status; rejects invalid alters | Active |
| R-073 | Prompt packet missing load-bearing alter details | Medium | High | P4-M1R: prompt packets include the complete loaded alter YAML and assert full_context_injected=true; list endpoint remains metadata-only | Mitigated |
| R-074 | Frontend later triggering writes through dialogue endpoint | Low | High | P4-M1: boundary_confirmations read_only=true, controlled_persist_called=false; endpoint has no write capability | Mitigated |
| R-075 | Reality scores inferred instead of explicitly submitted | Medium | High | P4-M2: request schema requires submitted_by_user=true and source=explicit_user_submission; extra provider/runtime fields are rejected | Mitigated |
| R-076 | Drift evidence triggering automatic regeneration | Low | High | P4-M3: drift endpoint returns evidence_only=true, regeneration_triggered=false, and performs no writes | Mitigated |
| R-077 | Calibration history mutating score records | Low | Medium | P4-M4: history endpoint only reads score files and derives drift in memory; tests verify file contents unchanged | Mitigated |
| R-078 | Calibration loop modifying rubric or active YAML | Low | High | P4-M2/M3/M4 write only score records under alters/calibration/scores; no endpoint writes alters/current/** or rubric.yaml | Mitigated |
| R-079 | rubric suggestion mistaken for confirmed rubric | Medium | High | P4-M5 suggestions stay pending_review, rubric_write_allowed=false, and rubric.yaml is never written | Mitigated |
| R-080 | archive creation mistaken for rollback execution | Medium | High | P4-M6 archive packages are copy-only evidence; rollback notes require manual explicit review | Mitigated |
| R-081 | checkpoint plan mistaken for active regeneration | Medium | High | P4-M7 plans set regeneration_allowed_now=false, active_write_allowed=false, and every step execution_allowed_now=false | Mitigated |
| R-082 | runtime archive artifacts accidentally committed | Medium | High | Runtime archive/suggestion/checkpoint records are gitignored; only .gitkeep/_template.yaml may be tracked | Active |
| R-083 | phase4 closeout mistaken for full product completion | Medium | High | P4-CLOSEOUT report states backend calibration loop sealed candidate only; P5-000 remains blocked | Active |
| R-084 | provider/frontend/database scope creep after closeout | Medium | High | Phase 4 closeout checks no provider/frontend/database implementation and keeps P5-000 blocked pending GPT/human review | Active |
| R-085 | Provider secret leakage | Low | Critical | P5-M2: API keys never returned by API, redacted in logs, not written to disk. Config status returns "[redacted]" | Mitigated |
| R-086 | Frontend calling dangerous endpoint | Low | Critical | P5-M4: Frontend only calls safe product APIs. Grep tests verify no references to promotion-live-execution, branches/persist, alters/persist, or API key env names | Mitigated |
| R-087 | Provider output mistaken for truth | Medium | High | P5-M3: Provider replies include safety metadata. Dialogues are simulated. Sessions include provider_output_not_fact=true | Mitigated |
| R-088 | Provider output auto-persisted | Low | High | P5-M3: save_session defaults to false. Explicit opt-in required. Sessions written to ignored runtime area only | Mitigated |
| R-089 | Frontend triggering active mutation | Low | Critical | P5-M4: No frontend page calls promotion-live-execution, controlled persist, or archive create. API requires explicit confirmation | Mitigated |
| R-090 | Database migration scope creep | Medium | Medium | P5-M5: YAML remains default. Storage boundary explicitly states database_implemented=false. No DB imports in codebase | Mitigated |
| R-091 | Local MVP mistaken for production product | Medium | High | P5-M8: Release candidate docs clearly state single-user, local-only. No cloud deployment, no production auth, no billing | Active |
| R-092 | P6 becomes another analysis tool without behavior change | Medium | Critical | P6 success = behavior change, not feature completion. 4-week validation window required. Usage integrity audit before redesign. | Active |
| R-093 | Weekly review becomes too heavy and stops being used | Medium | High | Medium template (5-7 facts, 3 sentences max subjective). 30-60 min sessions. Skip-with-reason allowed. | Active |
| R-094 | User softens negative evidence during extraction edits | Medium | High | Extraction edit challenge triggers on lowering self_deception_risk, changing failure status, deleting negative facts. Challenge question: "这是事实修正，还是叙事软化？" | Active |
| R-095 | Provider output mistaken for truth | Medium | High | Provider default disabled/mock. Real provider requires explicit config. Provider output cannot auto-write active YAML or auto-generate reality score. | Active |
| R-096 | Obsidian notes become performative | Medium | High | System cannot invent facts. Raw note preserved. Dual-layer truth with raw note as primary. | Active |
| R-097 | Action alignment gamed by easy corrections | Low | High | Required evidence: one_action_evidence, one_avoidance_or_friction_evidence. Supporting actions must serve primary correction, not create new fronts. | Active |
| R-098 | Pattern constraints feel too restrictive and cause abandonment | Medium | High | Strategy constraints only trigger on 3+ occurrences in 4 weeks with high confidence. Next week primary correction must reflect constraint. | Active |
| R-099 | P6 mistakenly sealed after code completion without real use | Medium | Critical | P6_CODE_COMPLETE != P6_BEHAVIOR_VALIDATED. 4 weekly reviews, 4 calibration records, 1 monthly pattern review, measurable change required before sealing. | Active |
| R-100 | Raw P6 runtime records accidentally committed | Medium | High | P6 runtime directories under alters/product are gitignored; only .gitkeep/template and sanitized evidence should be tracked. Phase 6 closeout checks git-tracked P6 runtime paths. | Active |
| R-101 | Behavior validation forged with arbitrary IDs | Medium | Critical | P6-CODE-COMPLETE-R1 verifies persisted weekly review, calibration, and pattern records, requires a 4-week window, and makes closeout re-verify latest validation evidence. | Mitigated |
| R-102 | Endgame automation mistaken for behavior validation | Medium | Critical | Keep code complete, validation, and closeout as separate states. Helper scripts print BLOCKED when evidence is incomplete and do not mark P6 sealed. | Active |
| R-103 | Package install overwrites user data | Medium | Critical | `.deb` package installs app code only; config, secrets, runtime data, and logs remain user-owned and preserved on upgrade/uninstall. | Active |
| R-104 | Provider secrets leaked through config, API, or logs | Medium | Critical | Provider defaults disabled/mock; real provider explicit; secrets stored in keyring or chmod 0600 fallback; API/status/logs redact keys. | Active |
| R-105 | Frontend calls dangerous endpoints | Medium | Critical | Frontend policy forbids controlled persist, promotion live execution, and active mutation endpoints; P7-M2/M4 must include route safety checks. | Active |
| R-106 | Packaged mode writes into repo paths | Medium | High | P7-M1 added runtime layout resolver and tests proving packaged writes go to `~/.local/share/alters-lab/product` or an overridden test data dir; explicit repo_root preserves dev behavior. | Mitigated |
| R-107 | P7 mistaken for P6 behavior validation | Medium | Critical | P7 docs and governance state P7 enables real use only; P6 remains CODE_COMPLETE / NOT_VALIDATED / NOT_SEALED until verified real evidence exists. | Active |
| R-108 | Local server exposed beyond localhost | Low | High | Packaged server binds to `127.0.0.1` by default; configurable host must be explicit and visible in doctor/status. | Active |
| R-109 | Upgrade breaks existing user data | Medium | High | P7-M7 must define upgrade/uninstall data-safety checks and backup/export behavior before release candidate. | Active |
| R-110 | Runtime config endpoint leaks provider secrets | Low | Critical | `/runtime-layout/status` returns provider mode/storage only with `secrets_redacted=true`; `/runtime-layout/ensure-config` writes config only and no secret values. | Active |
| R-111 | Frontend static mount shadows API routes | Medium | Critical | P7-M2 registers API routers before frontend fallback, blocks known API prefixes from SPA fallback, and adds route inventory/API preservation tests. | Mitigated |
| R-112 | Launcher leaves stale background processes or kills wrong process | Medium | High | P7-M3 stores launcher-owned PID metadata, cleans stale PID files, blocks non-Alters PID ownership, defaults to localhost, and tests not_running/stale_pid/port_conflict paths. | Mitigated |
| R-113 | Provider secrets may leak through API, logs, frontend, or committed files | Medium | Critical | P7-M4 returns only redacted secret status, never returns API key values, writes fallback secrets with chmod `0600`, clears the frontend key input after save, avoids localStorage, and requires secret grep before commit. | Active |
| R-114 | Package may accidentally include secrets, node_modules, raw runtime records, or user data | Medium | Critical | P7-M5 build script excludes node_modules, `.env`, `alters/product`, user home config/data/log paths, and secrets; tests cover exclusions; `.deb` artifacts are ignored; dpkg contents inspection required. | Active |

## Risk Assessment

- **Likelihood**: Low / Medium / High
- **Impact**: Low / Medium / High
- **Status**: Active / Mitigated / Closed
