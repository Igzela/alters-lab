"""P6-M11 closeout gate service.

Closeout is intentionally blocked until behavior validation passes with real
four-week evidence. Code completion alone cannot seal P6.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from alters_lab.schemas.phase6_closeout import (
    Phase6CloseoutCheck,
    Phase6CloseoutReportResponse,
    Phase6CloseoutSummary,
)
from alters_lab.services.behavior_validation import behavior_validation_has_verified_evidence, latest_behavior_validation
from alters_lab.services.p6_runtime import P6_RUNTIME_AREAS, get_repo_root


def _get_repo_root() -> Path:
    return get_repo_root()


def check_behavior_validation_passed(repo_root: Path | None = None) -> Phase6CloseoutCheck:
    validation = latest_behavior_validation(repo_root)
    if validation is None:
        return Phase6CloseoutCheck(
            name="behavior_validation_passed",
            status="FAIL",
            severity="critical",
            message="No behavior validation record exists.",
        )
    if behavior_validation_has_verified_evidence(validation, repo_root):
        return Phase6CloseoutCheck(
            name="behavior_validation_passed",
            status="PASS",
            severity="critical",
            message="Latest behavior validation outcome is P6_BEHAVIOR_VALIDATED and persisted evidence re-verifies.",
        )
    return Phase6CloseoutCheck(
        name="behavior_validation_passed",
        status="FAIL",
        severity="critical",
        message=f"Latest behavior validation outcome is {validation.outcome}; verified persisted evidence is required.",
    )


def check_no_active_yaml_diff(repo_root: Path | None = None) -> Phase6CloseoutCheck:
    root = repo_root or _get_repo_root()
    result = subprocess.run(["git", "diff", "--", "alters/current"], cwd=str(root), capture_output=True, text=True, timeout=10)
    if result.stdout.strip():
        return Phase6CloseoutCheck(name="no_active_yaml_diff", status="FAIL", severity="critical", message="Active YAML has uncommitted changes.")
    return Phase6CloseoutCheck(name="no_active_yaml_diff", status="PASS", severity="critical", message="No active YAML diff detected.")


def check_no_rubric_diff(repo_root: Path | None = None) -> Phase6CloseoutCheck:
    root = repo_root or _get_repo_root()
    result = subprocess.run(["git", "diff", "--", "alters/calibration/rubric.yaml"], cwd=str(root), capture_output=True, text=True, timeout=10)
    if result.stdout.strip():
        return Phase6CloseoutCheck(name="no_rubric_diff", status="FAIL", severity="critical", message="Rubric YAML has uncommitted changes.")
    return Phase6CloseoutCheck(name="no_rubric_diff", status="PASS", severity="critical", message="No rubric diff detected.")


def check_provider_default_safe() -> Phase6CloseoutCheck:
    mode = os.environ.get("ALTERS_PROVIDER_MODE", "mock")
    if mode in ("mock", "disabled"):
        return Phase6CloseoutCheck(name="provider_default_safe", status="PASS", severity="critical", message=f"Provider mode is {mode}.")
    return Phase6CloseoutCheck(name="provider_default_safe", status="FAIL", severity="critical", message=f"Provider mode is {mode}, not mock/disabled.")


def check_no_raw_p6_runtime_tracked(repo_root: Path | None = None) -> Phase6CloseoutCheck:
    root = repo_root or _get_repo_root()
    paths = list(P6_RUNTIME_AREAS.values())
    result = subprocess.run(["git", "ls-files", *paths], cwd=str(root), capture_output=True, text=True, timeout=10)
    tracked = [line for line in result.stdout.splitlines() if line.strip()]
    raw = [path for path in tracked if not path.endswith(".gitkeep") and "_template" not in path]
    if raw:
        return Phase6CloseoutCheck(name="no_raw_p6_runtime_tracked", status="FAIL", severity="critical", message=f"Raw P6 runtime files tracked: {raw}")
    return Phase6CloseoutCheck(name="no_raw_p6_runtime_tracked", status="PASS", severity="critical", message="No raw P6 runtime records tracked.")


def check_raw_note_source_policy() -> Phase6CloseoutCheck:
    from alters_lab.schemas.obsidian_weekly_note import WeeklyNoteExtractedRecord

    fields = WeeklyNoteExtractedRecord.model_fields
    required = {"raw_note", "raw_note_preserved", "derived_from_raw_note", "edit_history"}
    missing = sorted(required - set(fields))
    if missing:
        return Phase6CloseoutCheck(name="raw_note_source_policy", status="FAIL", severity="critical", message=f"Missing fields: {missing}")
    return Phase6CloseoutCheck(name="raw_note_source_policy", status="PASS", severity="critical", message="Weekly note records preserve raw note and edit history.")


def build_phase6_closeout_report(repo_root: Path | None = None) -> Phase6CloseoutReportResponse:
    checks = [
        check_behavior_validation_passed(repo_root),
        check_no_active_yaml_diff(repo_root),
        check_no_rubric_diff(repo_root),
        check_provider_default_safe(),
        check_no_raw_p6_runtime_tracked(repo_root),
        check_raw_note_source_policy(),
    ]
    passed = sum(1 for c in checks if c.status == "PASS")
    failed = sum(1 for c in checks if c.status == "FAIL")
    notes = sum(1 for c in checks if c.status == "NOTE")
    status = "PASS" if failed == 0 else "BLOCKED"
    summary = Phase6CloseoutSummary(
        overall_status=status,
        total_checks=len(checks),
        passed=passed,
        failed=failed,
        notes=notes,
        sealed_baseline_candidate=status == "PASS",
    )
    return Phase6CloseoutReportResponse(status=status, summary=summary, checks=checks)
