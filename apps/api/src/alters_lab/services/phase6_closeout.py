"""P6-M11 closeout gate service.

Closeout is intentionally blocked until behavior validation passes with real
four-week evidence. Code completion alone cannot seal P6.
"""

from __future__ import annotations

from pathlib import Path

from alters_lab.schemas.phase6_closeout import (
    Phase6CloseoutCheck,
    Phase6CloseoutReportResponse,
    Phase6CloseoutSummary,
)
from alters_lab.services.behavior_validation import behavior_validation_has_verified_evidence, latest_behavior_validation
from alters_lab.services.closeout_base import (
    check_no_active_yaml_diff as _shared_no_active_yaml_diff,
    check_no_rubric_diff as _shared_no_rubric_diff,
    check_no_raw_runtime_artifacts,
    check_provider_default_safe as _shared_provider_default_safe,
    compute_summary,
    get_repo_root,
)
from alters_lab.services.p6_runtime import P6_RUNTIME_AREAS


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
    base = _shared_no_active_yaml_diff(root)
    return Phase6CloseoutCheck(
        name="no_active_yaml_diff",
        status=base.status,
        severity="critical",
        message=base.message,
    )


def check_no_rubric_diff(repo_root: Path | None = None) -> Phase6CloseoutCheck:
    root = repo_root or _get_repo_root()
    base = _shared_no_rubric_diff(root)
    return Phase6CloseoutCheck(
        name="no_rubric_diff",
        status=base.status,
        severity="critical",
        message=base.message,
    )


def check_provider_default_safe() -> Phase6CloseoutCheck:
    base = _shared_provider_default_safe()
    return Phase6CloseoutCheck(
        name="provider_default_safe",
        status=base.status,
        severity="critical",
        message=base.message,
    )


def check_no_raw_p6_runtime_tracked(repo_root: Path | None = None) -> Phase6CloseoutCheck:
    root = repo_root or _get_repo_root()
    base = check_no_raw_runtime_artifacts(
        root,
        list(P6_RUNTIME_AREAS.values()),
        check_name="no_raw_p6_runtime_tracked",
    )
    return Phase6CloseoutCheck(
        name="no_raw_p6_runtime_tracked",
        status=base.status,
        severity="critical",
        message=base.message,
    )


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
    summary_base = compute_summary(checks)
    summary = Phase6CloseoutSummary(
        overall_status=summary_base.status,
        total_checks=summary_base.total_checks,
        passed=summary_base.passed,
        failed=summary_base.failed,
        notes=summary_base.warnings,
        sealed_baseline_candidate=summary_base.status == "PASS",
    )
    return Phase6CloseoutReportResponse(status=summary_base.status, summary=summary, checks=checks)
