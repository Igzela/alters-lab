#!/usr/bin/env python3
"""P8 Provider Safety Audit.

Scans the repository for provider-related safety violations:
- Secrets (API keys, tokens)
- Provider output content in committed evidence
- Provider prompt/response content in committed files

Classifies findings as allowed (source references) vs disallowed
(evidence/runtime leaks). Produces summary evidence, not raw content.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

# Patterns to search for
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

REDACTED_EVIDENCE_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("redacted_provider_output", re.compile(r"\[redacted-provider-output\]")),
    ("redacted_prompt", re.compile(r"\[redacted-prompt\]")),
    ("redacted_secret", re.compile(r"\[redacted-secret\]")),
]

# Directories to skip
SKIP_DIRS = {
    ".git", "node_modules", ".venv", "venv", "dist", "build",
    "__pycache__", ".mypy_cache", ".pytest_cache", ".ruff_cache",
    "egg-info",
}

# File extensions to scan
SCAN_EXTENSIONS = {
    ".py", ".json", ".md", ".yaml", ".yml", ".toml", ".cfg",
    ".ts", ".tsx", ".js", ".jsx", ".html", ".css", ".sh",
}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="P8 Provider Safety Audit")
    parser.add_argument("--repo-root", default=".", help="Repository root path")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--evidence", default=None)
    return parser.parse_args(argv)


def _should_scan(path: Path) -> bool:
    """Check if a file should be scanned."""
    if path.suffix not in SCAN_EXTENSIONS:
        return False
    parts = path.parts
    return not any(skip in parts for skip in SKIP_DIRS)


def _classify_finding(path: Path, repo_root: Path) -> str:
    """Classify a finding by its file path.

    Returns a category string:
    - source_code: .py files in src/
    - test: test files
    - documentation: .md files
    - evidence_json: committed evidence JSON files
    - config: config/yaml/toml files
    - other: everything else
    """
    rel = path.relative_to(repo_root)
    parts = rel.parts
    suffix = path.suffix

    # Evidence JSON files in docs/harness are disallowed
    if "docs" in parts and "harness" in parts and suffix == ".json":
        return "evidence_json"

    # Test files
    if any(p.startswith("test_") for p in parts) or "tests" in parts:
        return "test"

    # Source code
    if "src" in parts and suffix == ".py":
        return "source_code"

    # Documentation
    if suffix == ".md":
        return "documentation"

    # Config files
    if suffix in {".yaml", ".yml", ".toml", ".cfg"}:
        return "config"

    # Tools directory
    if "tools" in parts:
        return "tool"

    return "other"


def scan_repo(repo_root: Path) -> dict[str, Any]:
    """Scan repository for provider safety violations.

    Returns a report dict with:
    - findings: list of {pattern_name, file_path, category, classification}
    - summary: counts by classification and category
    - status: PASS or FAIL
    """
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

    # Build summary
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

    status = "FAIL" if disallowed_count > 0 else "PASS"

    return {
        "status": status,
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
        "p6_behavior_validated": False,
        "p6_sealed": False,
    }


def _classify_result(category: str) -> str:
    """Determine if a finding category is allowed or disallowed."""
    allowed_categories = {"source_code", "test", "documentation", "config", "tool"}
    if category in allowed_categories:
        return "allowed"
    return "disallowed"


def assert_audit_passes(report: dict[str, Any]) -> None:
    """Assert that the audit found no disallowed findings."""
    assert report["status"] == "PASS", (
        f"Audit found {report['disallowed_count']} disallowed findings: "
        f"{report['disallowed_files']}"
    )
    assert report["p6_behavior_validated"] is False
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
        print(f"total_findings={report['total_findings']}")
        print(f"allowed={report['allowed_count']}")
        print(f"disallowed={report['disallowed_count']}")
        if report["disallowed_files"]:
            print(f"disallowed_files={report['disallowed_files']}")

    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
