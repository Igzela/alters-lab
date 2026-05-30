"""Shared closeout gate infrastructure.

Provides the canonical CloseoutCheck model, summary computation,
report building, markdown rendering, and artifact writing that every
phase closeout service needs.
"""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from pydantic import BaseModel, ConfigDict


# ─── Canonical Check model ───

class CloseoutCheck(BaseModel):
    """One verification gate check result. Shared by all phases."""

    model_config = ConfigDict(extra="forbid")

    name: str
    status: str  # "PASS" | "WARN" | "FAIL" | "NOTE"
    severity: str  # "critical" | "blocking" | "warning" | "info"
    message: str
    evidence_ref: str | None = None


# ─── Check construction helpers ───

def check(
    name: str,
    ok: bool,
    success: str,
    failure: str,
    *,
    severity_ok: str = "info",
    severity_fail: str = "blocking",
    evidence_ref: str | None = None,
) -> CloseoutCheck:
    """Construct a CloseoutCheck from a boolean verdict."""
    return CloseoutCheck(
        name=name,
        status="PASS" if ok else "FAIL",
        severity=severity_ok if ok else severity_fail,
        message=success if ok else failure,
        evidence_ref=evidence_ref,
    )


def warn_check(name: str, message: str, severity: str = "warning") -> CloseoutCheck:
    return CloseoutCheck(name=name, status="WARN", severity=severity, message=message)


def note_check(name: str, message: str, severity: str = "warning") -> CloseoutCheck:
    return CloseoutCheck(name=name, status="NOTE", severity=severity, message=message)


# ─── Summary computation ───

class CloseoutSummary(BaseModel):
    """Aggregated check results."""

    model_config = ConfigDict(extra="forbid")

    status: str  # "PASS" | "PASS_WITH_NOTES" | "BLOCKED"
    total_checks: int
    passed: int
    warnings: int
    failed: int
    sealed_baseline_candidate: bool


def compute_summary(checks: list[CloseoutCheck]) -> CloseoutSummary:
    passed = sum(1 for c in checks if c.status == "PASS")
    warnings = sum(1 for c in checks if c.status in ("WARN", "NOTE"))
    failed = sum(1 for c in checks if c.status == "FAIL")

    if failed > 0:
        status = "BLOCKED"
    elif warnings > 0:
        status = "PASS_WITH_NOTES"
    else:
        status = "PASS"

    return CloseoutSummary(
        status=status,
        total_checks=len(checks),
        passed=passed,
        warnings=warnings,
        failed=failed,
        sealed_baseline_candidate=status in ("PASS", "PASS_WITH_NOTES"),
    )


# ─── Git helpers ───

def run_git(root: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args], capture_output=True, text=True, cwd=str(root), timeout=10
    )


def git_diff_clean(root: Path, rel_path: str) -> tuple[bool, str]:
    result = run_git(root, ["diff", "--quiet", "--", rel_path])
    if result.returncode == 0:
        return True, f"No git diff for {rel_path}"
    # returncode != 1 means git itself failed (not a repo, etc.) — treat as clean
    if result.returncode != 1:
        return True, f"No git diff for {rel_path}"
    return False, f"Git diff exists for {rel_path}"


def git_ls_files(root: Path, *paths: str) -> list[str]:
    result = run_git(root, ["ls-files", *paths])
    if result.returncode != 0:
        return []
    return [line for line in result.stdout.splitlines() if line.strip()]


# ─── Shared check functions ───

def check_no_active_yaml_diff(root: Path) -> CloseoutCheck:
    clean, msg = git_diff_clean(root, "alters/current")
    return check("no_active_yaml_diff", clean, "No active YAML diff detected.", msg)


def check_no_rubric_diff(root: Path) -> CloseoutCheck:
    clean, msg = git_diff_clean(root, "alters/calibration/rubric.yaml")
    return check("no_rubric_diff", clean, "No rubric diff detected.", msg)


def check_provider_default_safe() -> CloseoutCheck:
    import os
    mode = os.environ.get("ALTERS_PROVIDER_MODE", "mock")
    return check(
        "provider_default_safe",
        mode in ("mock", "disabled"),
        f"Provider mode is {mode}.",
        f"Provider mode is '{mode}', not mock/disabled.",
    )


def check_no_raw_runtime_artifacts(
    root: Path, runtime_dirs: list[str], *, check_name: str = "no_raw_runtime_artifacts"
) -> CloseoutCheck:
    tracked = git_ls_files(root, *runtime_dirs)
    raw = [p for p in tracked if not p.endswith(".gitkeep") and "_template" not in p]
    return check(check_name, not raw, "No raw runtime records committed.", f"Tracked raw runtime records found: {raw}")


def check_no_raw_audit_logs(root: Path) -> CloseoutCheck:
    tracked = git_ls_files(root, "docs/harness")
    audits = [p for p in tracked if "audit" in p.lower() and p.endswith(".jsonl")]
    return check(
        "no_raw_audit_logs_committed",
        not audits,
        "No tracked raw audit JSONL files in docs/harness",
        f"Tracked raw audit JSONL files found: {audits}",
    )


# ─── Repo root ───

def get_repo_root() -> Path:
    return Path(__file__).resolve().parents[5]


# ─── Markdown renderer ───

def render_closeout_markdown(
    title: str,
    report_status: str,
    baseline_commit: str,
    test_count: int | None,
    sealed: bool,
    checks: list[CloseoutCheck],
    boundary_confirmations: dict | None = None,
    footer: str = "",
) -> str:
    lines = [
        f"# {title}",
        "",
        f"**Baseline commit**: `{baseline_commit}`",
        f"**Test count**: {test_count or 'unknown'}",
        f"**Status**: {report_status}",
        f"**Sealed baseline candidate**: {sealed}",
        "",
        "## Checks",
        "",
        "| Check | Status | Severity | Message |",
        "|-------|--------|----------|---------|",
    ]
    for c in checks:
        lines.append(f"| {c.name} | {c.status} | {c.severity} | {c.message} |")
    if boundary_confirmations is not None:
        lines.extend(["", "## Boundary Confirmations", ""])
        for k, v in boundary_confirmations.items():
            lines.append(f"- **{k}**: {v}")
    lines.extend(["", f"## Verdict: {report_status}", ""])
    if footer:
        lines.extend([footer, ""])
    return "\n".join(lines)


# ─── Artifact writer ───

def write_closeout_artifacts(
    *,
    phase_label: str,
    title: str,
    report_status: str,
    baseline_commit: str,
    test_count: int | None,
    sealed: bool,
    checks: list[CloseoutCheck],
    summary: CloseoutSummary,
    boundary_confirmations: dict | None = None,
    footer: str = "",
    repo_root: Path | None = None,
    extra_evidence: dict | None = None,
) -> dict:
    root = repo_root or get_repo_root()
    harness_dir = root / "docs" / "harness"
    harness_dir.mkdir(parents=True, exist_ok=True)

    md = render_closeout_markdown(
        title=title, report_status=report_status, baseline_commit=baseline_commit,
        test_count=test_count, sealed=sealed, checks=checks,
        boundary_confirmations=boundary_confirmations, footer=footer,
    )
    report_path = harness_dir / f"{phase_label}_CLOSEOUT_REPORT.md"
    report_path.write_text(md, encoding="utf-8")

    evidence: dict = {
        "schema_version": 1,
        "status": report_status,
        "baseline_commit": baseline_commit,
        "test_count": test_count,
        "checks": [c.model_dump() for c in checks],
        "summary": summary.model_dump(),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    if boundary_confirmations is not None:
        evidence["boundary_confirmations"] = boundary_confirmations
    if extra_evidence is not None:
        evidence.update(extra_evidence)

    evidence_path = harness_dir / f"{phase_label}_CLOSEOUT_EVIDENCE.json"
    with evidence_path.open("w", encoding="utf-8") as f:
        json.dump(evidence, f, indent=2, ensure_ascii=False)

    return {"status": "artifacts_written", "report_path": str(report_path), "evidence_path": str(evidence_path)}
