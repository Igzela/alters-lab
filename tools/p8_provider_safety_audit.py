#!/usr/bin/env python3
"""P8 Provider Safety Audit.

Scans the repository for provider-related safety violations across
multiple audit sections:
1. Grep scan — secrets and provider output in committed files
2. Route audit — expected API routes registered in main.py
3. Live constants — LIVE_CONFIRMATION constants in provider services
4. Schema safety — Literal-locked safety fields in schemas
5. Evidence contract — P8-M5 evidence has no provider output, p6 false flags
6. Secret policy — services don't use _fallback_get directly
7. Provider mutation boundary — provider services don't import mutation paths
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path
from typing import Any

# --- Patterns for grep scan ---

SECRET_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("api_key_env", re.compile(r"ALTERS_PROVIDER_API_KEY")),
    ("openai_key_env", re.compile(r"OPENAI_API_KEY")),
    ("anthropic_key_env", re.compile(r"ANTHROPIC_API_KEY")),
    ("openrouter_key_env", re.compile(r"OPENROUTER_API_KEY")),
    ("sk_prefix", re.compile(r"sk-[A-Za-z0-9]{10,}")),
]

PROVIDER_OUTPUT_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("mock_adapter_preview", re.compile(r"mock adapter preview", re.IGNORECASE)),
    ("mock_dialogue_preview", re.compile(r"mock dialogue preview", re.IGNORECASE)),
    ("mock_weekly_review_assistant", re.compile(r"mock weekly review assistant", re.IGNORECASE)),
    ("deterministic_placeholder", re.compile(r"deterministic placeholder", re.IGNORECASE)),
]

SKIP_DIRS = {
    ".git", "node_modules", ".venv", "venv", "dist", "build",
    "__pycache__", ".mypy_cache", ".pytest_cache", ".ruff_cache",
    "egg-info",
}

SCAN_EXTENSIONS = {
    ".py", ".json", ".md", ".yaml", ".yml", ".toml", ".cfg",
    ".ts", ".tsx", ".js", ".jsx", ".html", ".css", ".sh",
}

# --- Expected routes (P8 provider routes) ---

EXPECTED_ROUTES: list[str] = [
    "provider_adapter",
    "provider_connectivity",
    "provider_config",
    "provider_dialogue_preview",
    "weekly_review_assistant",
]

# --- Expected LIVE_CONFIRMATION constants ---

EXPECTED_LIVE_CONSTANTS: list[tuple[str, str]] = [
    ("provider_connectivity", "run-live-provider-connectivity-check"),
    ("provider_dialogue_preview", "run-live-provider-dialogue-preview"),
    ("weekly_review_assistant", "run-live-weekly-review-assistant"),
]

# --- Provider service files (for mutation boundary check) ---

PROVIDER_SERVICE_FILES = [
    "provider_adapter.py",
    "provider_config.py",
    "provider_connectivity.py",
    "provider_dialogue_preview.py",
    "provider_gateway.py",
    "provider_dialogue.py",
    "weekly_review_assistant.py",
]

# --- Mutation boundary: imports that provider services must NOT have ---

MUTATION_IMPORT_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("action_alignment_score_import", re.compile(
        r"from\s+alters_lab\.(services|api)\.action_alignment\s+import.*score",
        re.IGNORECASE,
    )),
    ("active_yaml_write_import", re.compile(
        r"from\s+alters_lab\.(services|api)\.(active_yaml|alters)\s+import.*(write|save|persist|create)",
        re.IGNORECASE,
    )),
    ("weekly_review_complete_import", re.compile(
        r"from\s+alters_lab\.(services|api)\.weekly_review\s+import.*(complete|finish|submit)",
        re.IGNORECASE,
    )),
]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="P8 Provider Safety Audit")
    parser.add_argument("--repo-root", default=".", help="Repository root path")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--evidence", default=None)
    return parser.parse_args(argv)


def _should_scan(path: Path) -> bool:
    if path.suffix not in SCAN_EXTENSIONS:
        return False
    parts = path.parts
    return not any(skip in parts for skip in SKIP_DIRS)


def _classify_finding(path: Path, repo_root: Path) -> str:
    rel = path.relative_to(repo_root)
    parts = rel.parts
    suffix = path.suffix

    if "docs" in parts and "harness" in parts and suffix == ".json":
        return "evidence_json"
    if any(p.startswith("test_") for p in parts) or "tests" in parts:
        return "test"
    if "src" in parts and suffix == ".py":
        return "source_code"
    if suffix == ".md":
        return "documentation"
    if suffix in {".yaml", ".yml", ".toml", ".cfg"}:
        return "config"
    if "tools" in parts:
        return "tool"
    return "other"


def _classify_result(category: str) -> str:
    allowed_categories = {"source_code", "test", "documentation", "config", "tool"}
    return "allowed" if category in allowed_categories else "disallowed"


# --- Section 1: Grep scan ---


def _scan_grep(repo_root: Path) -> dict[str, Any]:
    findings: list[dict[str, str]] = []
    all_patterns = SECRET_PATTERNS + PROVIDER_OUTPUT_PATTERNS

    for path in repo_root.rglob("*"):
        if not path.is_file() or not _should_scan(path):
            continue
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except (OSError, PermissionError):
            continue
        for pattern_name, compiled in all_patterns:
            if compiled.search(content):
                category = _classify_finding(path, repo_root)
                classification = _classify_result(category)
                findings.append({
                    "pattern": pattern_name,
                    "file": str(path.relative_to(repo_root)),
                    "category": category,
                    "classification": classification,
                })

    allowed_count = sum(1 for f in findings if f["classification"] == "allowed")
    disallowed_count = sum(1 for f in findings if f["classification"] == "disallowed")

    allowed_by_category: dict[str, int] = {}
    disallowed_by_category: dict[str, int] = {}
    allowed_by_pattern: dict[str, int] = {}
    disallowed_by_pattern: dict[str, int] = {}

    for f in findings:
        if f["classification"] == "allowed":
            allowed_by_category[f["category"]] = allowed_by_category.get(f["category"], 0) + 1
            allowed_by_pattern[f["pattern"]] = allowed_by_pattern.get(f["pattern"], 0) + 1
        else:
            disallowed_by_category[f["category"]] = disallowed_by_category.get(f["category"], 0) + 1
            disallowed_by_pattern[f["pattern"]] = disallowed_by_pattern.get(f["pattern"], 0) + 1

    return {
        "section": "grep_scan",
        "status": "FAIL" if disallowed_count > 0 else "PASS",
        "total_findings": len(findings),
        "allowed_count": allowed_count,
        "disallowed_count": disallowed_count,
        "allowed_by_category": allowed_by_category,
        "allowed_by_pattern": allowed_by_pattern,
        "disallowed_by_category": disallowed_by_category,
        "disallowed_by_pattern": disallowed_by_pattern,
        "disallowed_files": sorted(
            {f["file"] for f in findings if f["classification"] == "disallowed"}
        ),
    }


# --- Section 2: Route audit ---


def _scan_routes(repo_root: Path) -> dict[str, Any]:
    main_py = repo_root / "apps" / "api" / "src" / "alters_lab" / "main.py"
    if not main_py.exists():
        return {
            "section": "route_audit",
            "status": "FAIL",
            "error": "main.py not found",
        }

    content = main_py.read_text(encoding="utf-8")
    missing = []
    found = []
    for route in EXPECTED_ROUTES:
        if route in content:
            found.append(route)
        else:
            missing.append(route)

    return {
        "section": "route_audit",
        "status": "PASS" if not missing else "FAIL",
        "expected_routes": len(EXPECTED_ROUTES),
        "found_routes": len(found),
        "missing_routes": missing,
    }


# --- Section 3: Live constants audit ---


def _scan_live_constants(repo_root: Path) -> dict[str, Any]:
    services_dir = repo_root / "apps" / "api" / "src" / "alters_lab" / "services"
    if not services_dir.exists():
        return {
            "section": "live_constants",
            "status": "FAIL",
            "error": "services dir not found",
        }

    results = []
    for module_name, expected_value in EXPECTED_LIVE_CONSTANTS:
        service_file = services_dir / f"{module_name}.py"
        if not service_file.exists():
            results.append({
                "module": module_name,
                "status": "FAIL",
                "error": "file not found",
            })
            continue

        content = service_file.read_text(encoding="utf-8")
        pattern = re.compile(
            r"""LIVE_CONFIRMATION\s*=\s*["'](.+?)["']"""
        )
        match = pattern.search(content)
        if match and match.group(1) == expected_value:
            results.append({
                "module": module_name,
                "status": "PASS",
                "value": expected_value,
            })
        elif match:
            results.append({
                "module": module_name,
                "status": "FAIL",
                "error": f"value mismatch: got {match.group(1)!r}",
            })
        else:
            results.append({
                "module": module_name,
                "status": "FAIL",
                "error": "LIVE_CONFIRMATION not found",
            })

    all_pass = all(r["status"] == "PASS" for r in results)
    return {
        "section": "live_constants",
        "status": "PASS" if all_pass else "FAIL",
        "checks": results,
    }


# --- Section 4: Schema safety audit ---


PROVIDER_SCHEMA_FILES = [
    "provider_adapter.py",
    "provider_config.py",
    "provider_connectivity.py",
    "provider_dialogue_preview.py",
    "weekly_review_assistant.py",
]


def _scan_schema_safety(repo_root: Path) -> dict[str, Any]:
    schemas_dir = repo_root / "apps" / "api" / "src" / "alters_lab" / "schemas"
    if not schemas_dir.exists():
        return {
            "section": "schema_safety",
            "status": "FAIL",
            "error": "schemas dir not found",
        }

    critical_fields = {
        "behavior_validated",
        "p6_sealed",
        "active_yaml_modified",
        "rubric_modified",
        "output_persisted",
        "suggestion_persisted",
        "action_alignment_created",
        "reality_score_created",
        "prompt_persisted",
        "response_content_persisted",
    }

    issues = []
    files_checked = 0

    for schema_name in PROVIDER_SCHEMA_FILES:
        schema_file = schemas_dir / schema_name
        if not schema_file.exists():
            issues.append({"file": schema_name, "issue": "file not found"})
            continue
        content = schema_file.read_text(encoding="utf-8")
        files_checked += 1

        for field in critical_fields:
            if field in content:
                literal_pattern = re.compile(
                    rf"{field}\s*:\s*Literal\[(False|True)\]"
                )
                if not literal_pattern.search(content):
                    bool_pattern = re.compile(
                        rf"{field}\s*:\s*bool"
                    )
                    if bool_pattern.search(content):
                        issues.append({
                            "file": schema_name,
                            "field": field,
                            "issue": "uses bool instead of Literal",
                        })

    return {
        "section": "schema_safety",
        "status": "PASS" if not issues else "FAIL",
        "files_checked": files_checked,
        "issues": issues,
    }


# --- Section 5: Evidence contract ---


def _scan_evidence_contract(repo_root: Path) -> dict[str, Any]:
    evidence_path = repo_root / "docs" / "harness" / "P8_M5_E2E_PRODUCT_VALIDATION_EVIDENCE.json"
    if not evidence_path.exists():
        return {
            "section": "evidence_contract",
            "status": "SKIP",
            "error": "P8-M5 evidence not found",
        }

    content = evidence_path.read_text(encoding="utf-8")
    issues = []

    # Check for provider output content
    for pattern_name, compiled in PROVIDER_OUTPUT_PATTERNS:
        if compiled.search(content):
            issues.append(f"provider output pattern found: {pattern_name}")

    # Check behavior_validated
    try:
        data = json.loads(content)
        if data.get("behavior_validated") is not False:
            issues.append("behavior_validated is not False")
        if data.get("p6_sealed") is not False:
            issues.append("p6_sealed is not False")
    except json.JSONDecodeError:
        issues.append("evidence is not valid JSON")

    return {
        "section": "evidence_contract",
        "status": "PASS" if not issues else "FAIL",
        "issues": issues,
    }


# --- Section 6: Secret policy ---


def _scan_secret_policy(repo_root: Path) -> dict[str, Any]:
    services_dir = repo_root / "apps" / "api" / "src" / "alters_lab" / "services"
    if not services_dir.exists():
        return {
            "section": "secret_policy",
            "status": "FAIL",
            "error": "services dir not found",
        }

    issues = []
    for service_file in sorted(services_dir.glob("*.py")):
        if service_file.name.startswith("_"):
            continue
        content = service_file.read_text(encoding="utf-8")
        # _fallback_get should only be used inside provider_config.py
        if "_fallback_get" in content and service_file.name != "provider_config.py":
            issues.append({
                "file": service_file.name,
                "issue": "uses _fallback_get directly",
            })

    return {
        "section": "secret_policy",
        "status": "PASS" if not issues else "FAIL",
        "issues": issues,
    }


# --- Section 7: Provider mutation boundary ---


def _scan_mutation_boundary(repo_root: Path) -> dict[str, Any]:
    services_dir = repo_root / "apps" / "api" / "src" / "alters_lab" / "services"
    if not services_dir.exists():
        return {
            "section": "mutation_boundary",
            "status": "FAIL",
            "error": "services dir not found",
        }

    issues = []
    for service_name in PROVIDER_SERVICE_FILES:
        service_file = services_dir / service_name
        if not service_file.exists():
            continue
        content = service_file.read_text(encoding="utf-8")
        for pattern_name, compiled in MUTATION_IMPORT_PATTERNS:
            if compiled.search(content):
                issues.append({
                    "file": service_name,
                    "pattern": pattern_name,
                    "issue": "provider service imports mutation path",
                })

    return {
        "section": "mutation_boundary",
        "status": "PASS" if not issues else "FAIL",
        "issues": issues,
    }


# --- Main scan ---


def scan_repo(repo_root: Path) -> dict[str, Any]:
    sections = [
        _scan_grep(repo_root),
        _scan_routes(repo_root),
        _scan_live_constants(repo_root),
        _scan_schema_safety(repo_root),
        _scan_evidence_contract(repo_root),
        _scan_secret_policy(repo_root),
        _scan_mutation_boundary(repo_root),
    ]

    all_pass = all(s["status"] in ("PASS", "SKIP") for s in sections)
    failed_sections = [s["section"] for s in sections if s["status"] == "FAIL"]

    return {
        "status": "PASS" if all_pass else "FAIL",
        "sections": sections,
        "failed_sections": failed_sections,
        "behavior_validated": False,
        "p6_sealed": False,
    }


def assert_audit_passes(report: dict[str, Any]) -> None:
    assert report["status"] == "PASS", (
        f"Audit failed sections: {report.get('failed_sections')}"
    )
    assert report["behavior_validated"] is False
    assert report["p6_sealed"] is False


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    repo_root = Path(args.repo_root).expanduser().resolve()
    report = scan_repo(repo_root)

    if args.evidence:
        evidence_path = Path(args.evidence)
        evidence_path.parent.mkdir(parents=True, exist_ok=True)
        evidence_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"status={report['status']}")
        for section in report["sections"]:
            print(f"  {section['section']}: {section['status']}")

    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
