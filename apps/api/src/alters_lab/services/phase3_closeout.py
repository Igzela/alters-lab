"""Phase 3 Closeout Gate — read-only verification service."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from alters_lab.schemas.phase3_closeout import (
    Phase3CloseoutBoundaryConfirmations,
    Phase3CloseoutCheck,
    Phase3CloseoutReport,
    Phase3CloseoutSummary,
)
from alters_lab.services import io
from alters_lab.services.closeout_base import (
    check as _base_check,
    compute_summary,
    get_repo_root,
    git_ls_files,
    write_closeout_artifacts,
)


def phase3_closeout_boundary_confirmations() -> dict:
    return Phase3CloseoutBoundaryConfirmations().model_dump()


def check_active_yaml_chain() -> Phase3CloseoutCheck:
    from alters_lab.loaders.active_yaml import load_active_yaml_chain, validate_active_yaml_chain

    try:
        chain = load_active_yaml_chain()
        result = validate_active_yaml_chain(chain)
        ok = result.ok if hasattr(result, "ok") else result.get("ok", False)
    except Exception as e:
        return Phase3CloseoutCheck(
            name="active_yaml_chain",
            status="FAIL",
            severity="blocking",
            message=f"Active YAML chain validation error: {e}",
        )
    r = _base_check("active_yaml_chain", ok, "Active YAML chain valid", "Active YAML chain invalid")
    return Phase3CloseoutCheck(
        name=r.name, status=r.status, severity=r.severity, message=r.message,
    )


def check_phase3_evidence_files(repo_root: Path) -> Phase3CloseoutCheck:
    required = [
        "docs/harness/P3_M7_LIVE_PROMOTION_EVIDENCE.json",
        "docs/harness/PROJECT_BOARD.md",
        "docs/harness/TASK_QUEUE.md",
        "docs/harness/DECISION_RECORD.md",
        "docs/harness/RUN_LOG.md",
        "docs/harness/EVIDENCE_INDEX.md",
    ]
    missing = [f for f in required if not (repo_root / f).exists()]
    if missing:
        return Phase3CloseoutCheck(
            name="phase3_evidence_files",
            status="FAIL",
            severity="blocking",
            message=f"Missing evidence files: {', '.join(missing)}",
        )
    return Phase3CloseoutCheck(
        name="phase3_evidence_files",
        status="PASS",
        severity="info",
        message="All required Phase 3 evidence files present",
    )


def check_p3_m7_semantic_noop_evidence(repo_root: Path) -> Phase3CloseoutCheck:
    evidence_path = repo_root / "docs/harness/P3_M7_LIVE_PROMOTION_EVIDENCE.json"
    if not evidence_path.exists():
        return Phase3CloseoutCheck(
            name="p3_m7_semantic_noop_evidence",
            status="FAIL",
            severity="blocking",
            message="P3-M7 evidence file not found",
        )
    evidence = io.read_json(evidence_path)
    errors: list[str] = []
    if evidence.get("verdict") != "PASS":
        errors.append(f"verdict={evidence.get('verdict')}, expected PASS")
    if evidence.get("semantic_noop_result") != "PASS":
        errors.append(f"semantic_noop_result={evidence.get('semantic_noop_result')}")
    if evidence.get("active_chain_validation") != "PASS":
        errors.append(f"active_chain_validation={evidence.get('active_chain_validation')}")
    tests = evidence.get("tests", {})
    if tests.get("result") != "PASS":
        errors.append(f"tests.result={tests.get('result')}")
    if evidence.get("raw_token_committed") is not False:
        errors.append("raw_token_committed is not false")
    if evidence.get("raw_audit_committed") is not False:
        errors.append("raw_audit_committed is not false")
    if evidence.get("runtime_drafts_committed") is not False:
        errors.append("runtime_drafts_committed is not false")
    bc = evidence.get("boundary_confirmations", {})
    if bc.get("first_controlled_live_promotion_run_completed") is not True:
        errors.append("first_controlled_live_promotion_run_completed is not true")
    if bc.get("promotion_was_semantic_noop") is not True:
        errors.append("promotion_was_semantic_noop is not true")
    if errors:
        return Phase3CloseoutCheck(
            name="p3_m7_semantic_noop_evidence",
            status="FAIL",
            severity="blocking",
            message=f"P3-M7 evidence validation failed: {'; '.join(errors)}",
        )
    return Phase3CloseoutCheck(
        name="p3_m7_semantic_noop_evidence",
        status="PASS",
        severity="info",
        message="P3-M7 semantic no-op evidence validated",
    )


def check_smuggling_boundary_restored() -> Phase3CloseoutCheck:
    from alters_lab.schemas.alters import (
        AlterBatchPersistRequest,
        AlterPersistRequest,
        AlterPayload,
    )
    from alters_lab.schemas.branches import (
        BranchDiscoveryPayload,
        BranchDiscoveryStatus,
        BranchesPersistRequest,
    )

    models = [
        ("AlterPayload", AlterPayload),
        ("AlterPersistRequest", AlterPersistRequest),
        ("AlterBatchPersistRequest", AlterBatchPersistRequest),
        ("BranchDiscoveryStatus", BranchDiscoveryStatus),
        ("BranchDiscoveryPayload", BranchDiscoveryPayload),
        ("BranchesPersistRequest", BranchesPersistRequest),
    ]
    failed = []
    for name, model in models:
        extra = model.model_config.get("extra")
        if extra != "forbid":
            failed.append(f"{name}.extra={extra}")
    if failed:
        return Phase3CloseoutCheck(
            name="smuggling_boundary_restored",
            status="FAIL",
            severity="blocking",
            message=f"Smuggling boundary not restored: {', '.join(failed)}",
        )
    return Phase3CloseoutCheck(
        name="smuggling_boundary_restored",
        status="PASS",
        severity="info",
        message="All API boundary models use extra='forbid'",
    )


def check_raw_dict_repersist_path_exists() -> Phase3CloseoutCheck:
    from alters_lab.services.alters_persist import (
        validate_alter_raw_dict,
        write_alter_raw_batch_with_audit,
    )
    from alters_lab.services.branches_persist import write_branches_raw_with_audit

    missing = []
    for fn_name, fn in [
        ("write_branches_raw_with_audit", write_branches_raw_with_audit),
        ("validate_alter_raw_dict", validate_alter_raw_dict),
        ("write_alter_raw_batch_with_audit", write_alter_raw_batch_with_audit),
    ]:
        if not callable(fn):
            missing.append(fn_name)
    if missing:
        return Phase3CloseoutCheck(
            name="raw_dict_repersist_path_exists",
            status="FAIL",
            severity="blocking",
            message=f"Missing raw dict functions: {', '.join(missing)}",
        )
    return Phase3CloseoutCheck(
        name="raw_dict_repersist_path_exists",
        status="PASS",
        severity="info",
        message="Raw dict re-persist path functions exist",
    )


def check_live_execution_default_safe() -> Phase3CloseoutCheck:
    from alters_lab.api import promotion_live_execution as live_api

    enabled = getattr(live_api, "LIVE_EXECUTION_ENABLED", False)
    if enabled:
        return Phase3CloseoutCheck(
            name="live_execution_default_safe",
            status="WARN",
            severity="warning",
            message="LIVE_EXECUTION_ENABLED is True — should be False by default",
        )
    return Phase3CloseoutCheck(
        name="live_execution_default_safe",
        status="PASS",
        severity="info",
        message="Live execution disabled by default",
    )


def check_no_runtime_artifacts_committed(repo_root: Path) -> Phase3CloseoutCheck:
    import subprocess

    drafts_dir = repo_root / "alters" / "drafts"

    # Check if any drafts are tracked by git
    try:
        result = subprocess.run(
            ["git", "ls-files", "alters/drafts"],
            capture_output=True,
            text=True,
            cwd=str(repo_root),
            timeout=10,
        )
        tracked = result.stdout.strip().splitlines() if result.returncode == 0 else []
    except Exception:
        tracked = []

    if tracked:
        return Phase3CloseoutCheck(
            name="no_runtime_artifacts_committed",
            status="FAIL",
            severity="blocking",
            message=f"Tracked runtime drafts found: {len(tracked)} files",
            evidence_ref="alters/drafts",
        )

    # Check for local (untracked/ignored) drafts
    if drafts_dir.exists():
        files = list(drafts_dir.rglob("*"))
        real_files = [f for f in files if f.is_file()]
        if real_files:
            return Phase3CloseoutCheck(
                name="no_runtime_artifacts_committed",
                status="WARN",
                severity="warning",
                message=f"Local runtime drafts exist ({len(real_files)} files); properly gitignored",
                evidence_ref=str(drafts_dir),
            )

    return Phase3CloseoutCheck(
        name="no_runtime_artifacts_committed",
        status="PASS",
        severity="info",
        message="No runtime draft artifacts found",
    )


def check_no_raw_audit_logs_committed(repo_root: Path) -> Phase3CloseoutCheck:
    harness_dir = repo_root / "docs" / "harness"
    if not harness_dir.exists():
        return Phase3CloseoutCheck(
            name="no_raw_audit_logs_committed",
            status="PASS",
            severity="info",
            message="No harness directory found",
        )

    tracked = git_ls_files(repo_root, "docs/harness")
    tracked_audits = [f for f in tracked if "audit" in f.lower() and f.endswith(".jsonl")]

    if tracked_audits:
        return Phase3CloseoutCheck(
            name="no_raw_audit_logs_committed",
            status="FAIL",
            severity="blocking",
            message=f"Tracked raw audit logs found: {tracked_audits}",
        )

    local_audits = list(harness_dir.glob("*audit*.jsonl"))
    if local_audits:
        return Phase3CloseoutCheck(
            name="no_raw_audit_logs_committed",
            status="WARN",
            severity="warning",
            message=f"Local untracked audit files exist: {[f.name for f in local_audits]}; not committed to git",
        )

    return Phase3CloseoutCheck(
        name="no_raw_audit_logs_committed",
        status="PASS",
        severity="info",
        message="No raw audit logs found in docs/harness",
    )


def check_phase3_governance_status(repo_root: Path) -> Phase3CloseoutCheck:
    errors: list[str] = []
    project_board = repo_root / "docs" / "harness" / "PROJECT_BOARD.md"
    if project_board.exists():
        content = project_board.read_text(encoding="utf-8")
        for required in ["P3-M6R2", "P3-M7", "done"]:
            if required not in content:
                errors.append(f"PROJECT_BOARD.md missing '{required}'")
    else:
        errors.append("PROJECT_BOARD.md not found")
    task_queue = repo_root / "docs" / "harness" / "TASK_QUEUE.md"
    if task_queue.exists():
        content = task_queue.read_text(encoding="utf-8")
        for required in [
            "First Human-Approved Live Promotion Run",
            "Raw Dict Re-persist Preserves Extras",
        ]:
            if required not in content:
                errors.append(f"TASK_QUEUE.md missing '{required}'")
    else:
        errors.append("TASK_QUEUE.md not found")
    if errors:
        return Phase3CloseoutCheck(
            name="phase3_governance_status",
            status="FAIL",
            severity="blocking",
            message=f"Governance docs incomplete: {'; '.join(errors)}",
        )
    return Phase3CloseoutCheck(
        name="phase3_governance_status",
        status="PASS",
        severity="info",
        message="Phase 3 governance docs complete",
    )


def build_phase3_closeout_report(
    repo_root: Path | None = None,
    baseline_commit: str = "unknown",
    test_count: int | None = None,
) -> Phase3CloseoutReport:
    root = repo_root or get_repo_root()

    checks = [
        check_active_yaml_chain(),
        check_phase3_evidence_files(root),
        check_p3_m7_semantic_noop_evidence(root),
        check_smuggling_boundary_restored(),
        check_raw_dict_repersist_path_exists(),
        check_live_execution_default_safe(),
        check_no_runtime_artifacts_committed(root),
        check_no_raw_audit_logs_committed(root),
        check_phase3_governance_status(root),
    ]

    summary = compute_summary(checks)
    sealed = summary.sealed_baseline_candidate
    next_status = "pending_human_gpt_review" if sealed else "blocked"

    phase_summary = Phase3CloseoutSummary(
        status=summary.status,
        total_checks=summary.total_checks,
        passed_checks=summary.passed,
        warning_checks=summary.warnings,
        failed_checks=summary.failed,
        sealed_baseline_candidate=sealed,
        next_phase_status=next_status,
    )

    return Phase3CloseoutReport(
        status=summary.status,
        baseline_commit=baseline_commit,
        test_count=test_count,
        checks=checks,
        summary=phase_summary,
        boundary_confirmations=Phase3CloseoutBoundaryConfirmations(),
        created_at=datetime.now(timezone.utc).isoformat(),
    )


def write_phase3_closeout_artifacts(
    report: Phase3CloseoutReport,
    repo_root: Path | None = None,
) -> dict:
    root = repo_root or get_repo_root()
    next_status = report.summary.next_phase_status
    return write_closeout_artifacts(
        phase_label="PHASE3",
        title="Phase 3 Controlled Mutation Closeout Report",
        report_status=report.status,
        baseline_commit=report.baseline_commit,
        test_count=report.test_count,
        sealed=report.summary.sealed_baseline_candidate,
        checks=report.checks,
        summary=compute_summary(report.checks),
        boundary_confirmations=report.boundary_confirmations.model_dump(),
        footer=f"Next phase status: {next_status}",
        repo_root=root,
    )
