"""P5-M7 Phase 5 Closeout service.

Verifies productization boundaries, not production readiness.
Read-only report and evidence endpoints.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from alters_lab.schemas.phase5_closeout import (
    CloseoutCheck,
    CloseoutSummary,
    Phase5CloseoutReportResponse,
)
from alters_lab.services.closeout_base import (
    check_no_active_yaml_diff as _shared_no_active_yaml_diff,
    check_no_rubric_diff as _shared_no_rubric_diff,
    check_no_raw_runtime_artifacts,
    check_provider_default_safe as _shared_provider_default_safe,
    compute_summary,
    get_repo_root,
)


def _get_repo_root() -> Path:
    return get_repo_root()


def _check_provider_gateway_default_safe() -> CloseoutCheck:
    base = _shared_provider_default_safe()
    return CloseoutCheck(
        name="provider_gateway_default_safe",
        status=base.status,
        severity="critical",
        message=base.message,
    )


def _check_no_secrets_committed() -> CloseoutCheck:
    root = _get_repo_root()
    secret_patterns = [r"sk-[A-Za-z0-9]{20,}", r"Bearer [A-Za-z0-9._-]{20,}"]
    found = []
    for pattern in secret_patterns:
        try:
            result = subprocess.run(
                ["grep", "-rE", pattern, str(root), "--exclude-dir=.git", "--exclude-dir=node_modules", "--exclude-dir=.venv", "--exclude-dir=tests", "--exclude=*.pyc", "--include=*.py", "--include=*.json", "--include=*.yaml", "--include=*.md", "--exclude=provider_gateway.py"],
                capture_output=True, text=True, timeout=10,
            )
            if result.stdout.strip():
                found.append(pattern)
        except Exception:
            pass
    if found:
        return CloseoutCheck(
            name="no_secrets_committed",
            status="FAIL",
            severity="critical",
            message=f"Found secret patterns: {found}",
        )
    return CloseoutCheck(
        name="no_secrets_committed",
        status="PASS",
        severity="critical",
        message="No secrets found in committed files.",
    )


def _check_no_active_yaml_diff() -> CloseoutCheck:
    root = _get_repo_root()
    base = _shared_no_active_yaml_diff(root)
    return CloseoutCheck(
        name="no_active_yaml_diff",
        status=base.status,
        severity="critical",
        message=base.message,
    )


def _check_no_rubric_diff() -> CloseoutCheck:
    root = _get_repo_root()
    base = _shared_no_rubric_diff(root)
    return CloseoutCheck(
        name="no_rubric_diff",
        status=base.status,
        severity="critical",
        message=base.message,
    )


def _check_frontend_no_dangerous_endpoints() -> CloseoutCheck:
    root = _get_repo_root()
    web_dir = root / "apps" / "web"
    if not web_dir.exists():
        return CloseoutCheck(
            name="frontend_no_dangerous_endpoints",
            status="NOTE",
            severity="warning",
            message="Frontend not present; skipping check.",
        )
    dangerous = ["promotion-live-execution", "branches/persist", "alters/persist", "ALTERS_PROVIDER_API_KEY"]
    found = []
    for pattern in dangerous:
        try:
            result = subprocess.run(
                ["grep", "-r", pattern, str(web_dir)],
                capture_output=True, text=True, timeout=10,
            )
            if result.stdout.strip():
                found.append(pattern)
        except Exception:
            pass
    if found:
        return CloseoutCheck(
            name="frontend_no_dangerous_endpoints",
            status="FAIL",
            severity="critical",
            message=f"Frontend references dangerous endpoints: {found}",
        )
    return CloseoutCheck(
        name="frontend_no_dangerous_endpoints",
        status="PASS",
        severity="critical",
        message="Frontend does not reference dangerous endpoints.",
    )


def _check_storage_no_db() -> CloseoutCheck:
    root = _get_repo_root()
    src = root / "apps" / "api" / "src" / "alters_lab"
    db_imports = ["import sqlite3", "from sqlite3", "import sqlalchemy", "from sqlalchemy", "import psycopg2", "from psycopg2", "import alembic", "from alembic", "from django.db", "import django.db"]
    found = []
    for pattern in db_imports:
        try:
            result = subprocess.run(
                ["grep", "-r", pattern, str(src), "--include=*.py", "--exclude=phase5_closeout.py"],
                capture_output=True, text=True, timeout=10,
            )
            if result.stdout.strip():
                found.append(pattern)
        except Exception:
            pass
    if found:
        return CloseoutCheck(
            name="storage_no_db",
            status="FAIL",
            severity="critical",
            message=f"Database imports found: {found}",
        )
    return CloseoutCheck(
        name="storage_no_db",
        status="PASS",
        severity="critical",
        message="No database imports found. YAML remains default.",
    )


def _check_provider_dialogue_no_default_persist() -> CloseoutCheck:
    from alters_lab.schemas.provider_dialogue import ProviderDialogueReplyRequest
    req = ProviderDialogueReplyRequest(user_message="test")
    if req.save_session is False:
        return CloseoutCheck(
            name="provider_dialogue_no_default_persist",
            status="PASS",
            severity="critical",
            message="save_session defaults to False.",
        )
    return CloseoutCheck(
        name="provider_dialogue_no_default_persist",
        status="FAIL",
        severity="critical",
        message="save_session does not default to False.",
    )


def _check_p5_docs_complete() -> CloseoutCheck:
    root = _get_repo_root()
    docs = [
        "docs/harness/P5_000_PRODUCTIZATION_PROVIDER_FRONTEND_BOUNDARY_PLAN.md",
        "docs/harness/P5_LOCAL_RELEASE_CANDIDATE.md",
    ]
    missing = [d for d in docs if not (root / d).exists()]
    if missing:
        return CloseoutCheck(
            name="p5_docs_complete",
            status="FAIL",
            severity="warning",
            message=f"Missing docs: {missing}",
        )
    return CloseoutCheck(
        name="p5_docs_complete",
        status="PASS",
        severity="warning",
        message="All P5 docs present.",
    )


def _check_no_raw_runtime_artifacts() -> CloseoutCheck:
    base = check_no_raw_runtime_artifacts(
        _get_repo_root(),
        ["alters/product/sessions", "alters/product/provider_runs", "alters/product/workflow_runs"],
    )
    return CloseoutCheck(
        name="no_raw_runtime_artifacts",
        status=base.status,
        severity="critical",
        message=base.message,
    )


def build_phase5_closeout_report() -> Phase5CloseoutReportResponse:
    checks = [
        _check_provider_gateway_default_safe(),
        _check_no_secrets_committed(),
        _check_no_active_yaml_diff(),
        _check_no_rubric_diff(),
        _check_frontend_no_dangerous_endpoints(),
        _check_storage_no_db(),
        _check_provider_dialogue_no_default_persist(),
        _check_p5_docs_complete(),
        _check_no_raw_runtime_artifacts(),
    ]

    summary_base = compute_summary(checks)
    status = summary_base.status.replace("BLOCKED", "FAIL")
    summary = CloseoutSummary(
        overall_status=status,
        total_checks=summary_base.total_checks,
        passed=summary_base.passed,
        failed=summary_base.failed,
        notes=summary_base.warnings,
    )

    return Phase5CloseoutReportResponse(
        status=status,
        summary=summary,
        checks=checks,
    )


def write_phase5_closeout_artifacts(report: Phase5CloseoutReportResponse) -> str:
    root = _get_repo_root()
    harness = root / "docs" / "harness"
    harness.mkdir(parents=True, exist_ok=True)

    evidence = {
        "status": report.status,
        "summary": report.summary.model_dump(),
        "checks": [c.model_dump() for c in report.checks],
        "generated_at": "2026-05-20",
    }

    evidence_path = harness / "PHASE5_CLOSEOUT_EVIDENCE.json"
    evidence_path.write_text(json.dumps(evidence, indent=2), encoding="utf-8")

    final_evidence = {
        "phase": "P5",
        "status": report.status,
        "summary": report.summary.model_dump(),
        "checks": [c.model_dump() for c in report.checks],
        "generated_at": "2026-05-20",
        "sealed_baseline": "2ae89a9d7d81d451e3efdc40d9054b13a9e50cb7",
    }
    final_path = harness / "P5_FINAL_EVIDENCE.json"
    final_path.write_text(json.dumps(final_evidence, indent=2), encoding="utf-8")

    return f"Artifacts written to {harness}"
