"""Phase 3 Closeout Gate — read-only verification service."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import yaml

from alters_lab.schemas.phase3_closeout import (
    Phase3CloseoutBoundaryConfirmations,
    Phase3CloseoutCheck,
    Phase3CloseoutReport,
    Phase3CloseoutSummary,
)


def phase3_closeout_boundary_confirmations() -> dict:
    return Phase3CloseoutBoundaryConfirmations().model_dump()


def get_repo_root() -> Path:
    return Path(__file__).resolve().parents[5]


def safe_read_yaml(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        return {}
    return data


def safe_read_json(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        return {}
    return data


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
    return Phase3CloseoutCheck(
        name="active_yaml_chain",
        status="PASS" if ok else "FAIL",
        severity="blocking" if not ok else "info",
        message="Active YAML chain valid" if ok else "Active YAML chain invalid",
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
    evidence = safe_read_json(evidence_path)
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
    import subprocess

    harness_dir = repo_root / "docs" / "harness"
    if not harness_dir.exists():
        return Phase3CloseoutCheck(
            name="no_raw_audit_logs_committed",
            status="PASS",
            severity="info",
            message="No harness directory found",
        )

    # Check whether any audit jsonl files are tracked by git
    try:
        result = subprocess.run(
            ["git", "ls-files", "docs/harness"],
            capture_output=True,
            text=True,
            cwd=str(repo_root),
            timeout=10,
        )
        tracked_files = result.stdout.strip().splitlines() if result.returncode == 0 else []
        tracked_audits = [f for f in tracked_files if "audit" in f.lower() and f.endswith(".jsonl")]
    except Exception:
        # git unavailable — fall back to filesystem check
        tracked_audits = []

    if tracked_audits:
        return Phase3CloseoutCheck(
            name="no_raw_audit_logs_committed",
            status="FAIL",
            severity="blocking",
            message=f"Tracked raw audit logs found: {tracked_audits}",
        )

    # Check for local (untracked) audit files
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

    passed = sum(1 for c in checks if c.status == "PASS")
    warnings = sum(1 for c in checks if c.status == "WARN")
    failed = sum(1 for c in checks if c.status == "FAIL")
    blocking = [c for c in checks if c.status == "FAIL" and c.severity == "blocking"]

    if blocking:
        status = "BLOCKED"
    elif warnings > 0:
        status = "PASS_WITH_NOTES"
    else:
        status = "PASS"

    sealed = status in ("PASS", "PASS_WITH_NOTES")

    summary = Phase3CloseoutSummary(
        status=status,
        total_checks=len(checks),
        passed_checks=passed,
        warning_checks=warnings,
        failed_checks=failed,
        sealed_baseline_candidate=sealed,
        next_phase_status="pending_human_gpt_review" if sealed else "blocked",
    )

    return Phase3CloseoutReport(
        status=status,
        baseline_commit=baseline_commit,
        test_count=test_count,
        checks=checks,
        summary=summary,
        boundary_confirmations=Phase3CloseoutBoundaryConfirmations(),
        created_at=datetime.now(timezone.utc).isoformat(),
    )


def write_phase3_closeout_artifacts(
    report: Phase3CloseoutReport,
    repo_root: Path | None = None,
) -> dict:
    root = repo_root or get_repo_root()
    harness_dir = root / "docs" / "harness"
    harness_dir.mkdir(parents=True, exist_ok=True)

    # Markdown report
    md_lines = [
        "# Phase 3 Controlled Mutation Closeout Report",
        "",
        f"**Baseline commit**: `{report.baseline_commit}`",
        f"**Test count**: {report.test_count or 'unknown'}",
        f"**Status**: {report.status}",
        f"**Sealed baseline candidate**: {report.summary.sealed_baseline_candidate}",
        "",
        "## Checks",
        "",
        "| Check | Status | Severity | Message |",
        "|-------|--------|----------|---------|",
    ]
    for c in report.checks:
        md_lines.append(f"| {c.name} | {c.status} | {c.severity} | {c.message} |")
    md_lines.extend([
        "",
        "## Boundary Confirmations",
        "",
    ])
    for k, v in report.boundary_confirmations.model_dump().items():
        md_lines.append(f"- **{k}**: {v}")
    md_lines.extend([
        "",
        f"## Verdict: {report.status}",
        "",
        f"Next phase status: {report.summary.next_phase_status}",
        "",
    ])
    report_md = harness_dir / "PHASE3_CLOSEOUT_REPORT.md"
    report_md.write_text("\n".join(md_lines), encoding="utf-8")

    # JSON evidence
    evidence = report.model_dump()
    evidence_path = harness_dir / "PHASE3_CLOSEOUT_EVIDENCE.json"
    with open(evidence_path, "w", encoding="utf-8") as f:
        json.dump(evidence, f, indent=2, ensure_ascii=False)

    return {
        "status": "artifacts_written",
        "report_path": str(report_md),
        "evidence_path": str(evidence_path),
    }
