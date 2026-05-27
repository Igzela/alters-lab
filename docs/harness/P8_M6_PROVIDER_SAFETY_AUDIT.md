# P8-M6 Provider Safety Audit

## Summary

Scans the repository for provider-related safety violations. Classifies findings as allowed (source references) vs disallowed (evidence/runtime leaks). Produces summary evidence, not raw content.

## Architecture

```
tools/p8_provider_safety_audit.py
    → walk repo (skip .git, node_modules, .venv, dist, build)
    → scan .py, .json, .md, .yaml, .ts, .js, .sh files
    → match secret patterns (sk-, API_KEY env vars)
    → match provider output patterns (mock adapter preview, etc.)
    → classify by file path (source/test/doc/evidence/tool)
    → allowed vs disallowed
    → JSON summary + evidence file
```

## Files

| File | Purpose |
|------|---------|
| `tools/p8_provider_safety_audit.py` | Audit script with pattern matching and classification |
| `apps/api/tests/test_p8_provider_safety_audit.py` | 29 tests for classification, scanning, reporting |
| `docs/harness/P8_M6_PROVIDER_SAFETY_AUDIT_EVIDENCE.json` | Audit evidence (summary counts, no raw content) |

## Patterns Scanned

| Pattern | Type |
|---------|------|
| `sk-[A-Za-z0-9]{10,}` | Secret |
| `ALTERS_PROVIDER_API_KEY` | Secret env |
| `OPENAI_API_KEY` | Secret env |
| `ANTHROPIC_API_KEY` | Secret env |
| `OPENROUTER_API_KEY` | Secret env |
| `mock adapter preview` | Provider output |
| `mock dialogue preview` | Provider output |
| `mock weekly review assistant` | Provider output |
| `deterministic placeholder` | Provider output |

## Classification Rules

| File Location | Classification |
|---------------|----------------|
| `src/` .py files | allowed (source_code) |
| `tests/` or `test_*.py` | allowed (test) |
| `*.md` | allowed (documentation) |
| `*.yaml, *.toml, *.cfg` | allowed (config) |
| `tools/` | allowed (tool) |
| `docs/harness/*.json` | disallowed (evidence_json) |
| Everything else | disallowed (other) |

## Evidence Output

Evidence stores only summary counts and categories:
- `allowed_by_category` — counts per allowed category
- `allowed_by_pattern` — counts per pattern in allowed files
- `disallowed_by_category` — counts per disallowed category
- `disallowed_files` — file paths (no content)
- `status` — PASS or FAIL

No raw secret or provider output content in evidence.

## Safety Guarantees

| Guarantee | Enforcement |
|-----------|-------------|
| No real secrets | sk- pattern detection |
| No provider output in evidence | Pattern matching + classification |
| Source references allowed | Classification separates code from evidence |
| Evidence summary only | No raw content stored |
| P6 false flags | p6_behavior_validated=False, p6_sealed=False |
