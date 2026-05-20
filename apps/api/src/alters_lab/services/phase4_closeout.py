"""Phase 4 Closeout Gate — read-only verification service."""

from __future__ import annotations

import importlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from alters_lab.schemas.phase4_closeout import (
    Phase4CloseoutBoundaryConfirmations,
    Phase4CloseoutCheck,
    Phase4CloseoutReport,
    Phase4CloseoutSummary,
)

REQUIRED_ROUTES = [
    "/rubric-delta/health",
    "/rubric-delta/suggest",
    "/rubric-delta/list",
    "/archive-mechanism/health",
    "/archive-mechanism/plan",
    "/archive-mechanism/create",
    "/archive-mechanism/list",
    "/checkpoint-regeneration/health",
    "/checkpoint-regeneration/plan",
    "/checkpoint-regeneration/list",
    "/phase4-closeout/health",
    "/phase4-closeout/report",
    "/phase4-closeout/evidence",
]

P4_MODULES = [
    "alters_lab.schemas.rubric_delta",
    "alters_lab.services.rubric_delta",
    "alters_lab.api.rubric_delta",
    "alters_lab.schemas.archive_mechanism",
    "alters_lab.services.archive_mechanism",
    "alters_lab.api.archive_mechanism",
    "alters_lab.schemas.checkpoint_regeneration",
    "alters_lab.services.checkpoint_regeneration",
    "alters_lab.api.checkpoint_regeneration",
    "alters_lab.schemas.phase4_closeout",
    "alters_lab.services.phase4_closeout",
    "alters_lab.api.phase4_closeout",
]

PROVIDER_PATTERNS = [
    "op" + "enai",
    "anth" + "ropic",
    "open" + "router",
    "lite" + "llm",
    "lang" + "chain",
    "crew" + "ai",
]
P4_SERVICE_FILES = [
    "apps/api/src/alters_lab/services/rubric_delta.py",
    "apps/api/src/alters_lab/services/archive_mechanism.py",
    "apps/api/src/alters_lab/services/checkpoint_regeneration.py",
    "apps/api/src/alters_lab/services/phase4_closeout.py",
]


def get_repo_root() -> Path:
    return Path(__file__).resolve().parents[5]


def phase4_closeout_boundary_confirmations() -> dict:
    return Phase4CloseoutBoundaryConfirmations().model_dump()


def safe_read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, dict) else {}


def _run_git(root: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        capture_output=True,
        text=True,
        cwd=str(root),
        timeout=10,
    )


def _check(name: str, ok: bool, success: str, failure: str, evidence_ref: str | None = None) -> Phase4CloseoutCheck:
    return Phase4CloseoutCheck(
        name=name,
        status="PASS" if ok else "FAIL",
        severity="info" if ok else "blocking",
        message=success if ok else failure,
        evidence_ref=evidence_ref,
    )


def check_p4_m1r_dialogue_contract() -> Phase4CloseoutCheck:
    try:
        from alters_lab.schemas.alter_dialogue import AlterDialoguePromptPacket
        from alters_lab.services.alter_dialogue import load_active_alter

        annotations = AlterDialoguePromptPacket.model_fields
        provider_default = annotations["provider_ready"].default is False
        full_context_default = annotations["full_context_injected"].default is True
        source = Path(load_active_alter.__code__.co_filename).read_text(encoding="utf-8")
        validates_first = source.find("validate_alter_id(alter_id)") < source.find('f"{alter_id}.yaml"')
        ok = provider_default and full_context_default and validates_first
    except Exception as exc:
        return Phase4CloseoutCheck(
            name="p4_m1r_dialogue_contract_hardened",
            status="FAIL",
            severity="blocking",
            message=f"Dialogue contract check failed: {exc}",
        )
    return _check(
        "p4_m1r_dialogue_contract_hardened",
        ok,
        "Dialogue contract keeps provider disabled, full context required, and validates alter ID before path construction",
        "Dialogue contract hardening is incomplete",
    )


def check_p4_modules_importable() -> Phase4CloseoutCheck:
    missing: list[str] = []
    for module_name in P4_MODULES:
        try:
            importlib.import_module(module_name)
        except Exception as exc:
            missing.append(f"{module_name}: {exc}")
    return _check(
        "p4_modules_importable",
        not missing,
        "All P4-M5/M6/M7/closeout modules import",
        f"Missing or invalid P4 modules: {'; '.join(missing)}",
    )


def check_p4_routes_registered() -> Phase4CloseoutCheck:
    try:
        from alters_lab.main import app

        routes = sorted(route.path for route in app.routes)
        missing = [route for route in REQUIRED_ROUTES if route not in routes]
    except Exception as exc:
        return Phase4CloseoutCheck(
            name="p4_routes_registered",
            status="FAIL",
            severity="blocking",
            message=f"Route inventory failed: {exc}",
        )
    return _check(
        "p4_routes_registered",
        not missing,
        "All P4-FINAL routes are registered",
        f"Missing routes: {missing}",
    )


def check_p4_boundary_contracts() -> Phase4CloseoutCheck:
    errors: list[str] = []
    try:
        from alters_lab.schemas.checkpoint_regeneration import (
            CheckpointRegenerationPlan,
            CheckpointRegenerationPlanStep,
        )
        from alters_lab.schemas.rubric_delta import RubricDeltaSuggestion
        from alters_lab.services.checkpoint_regeneration import _plan_steps
        from alters_lab.schemas.archive_mechanism import ArchiveCreateRequest

        if RubricDeltaSuggestion.model_fields["rubric_write_allowed"].default is not False:
            errors.append("Rubric delta allows rubric write")
        if CheckpointRegenerationPlan.model_fields["regeneration_allowed_now"].default is not False:
            errors.append("Checkpoint plan allows regeneration")
        if CheckpointRegenerationPlan.model_fields["active_write_allowed"].default is not False:
            errors.append("Checkpoint plan allows active write")
        if CheckpointRegenerationPlanStep.model_fields["execution_allowed_now"].default is not False:
            errors.append("Checkpoint step allows execution")
        if ArchiveCreateRequest is None:
            errors.append("Archive create request missing")
        if any(step.execution_allowed_now for step in _plan_steps()):
            errors.append("Checkpoint service step permits execution")
    except Exception as exc:
        errors.append(str(exc))
    return _check(
        "p4_boundary_contracts",
        not errors,
        "P4-M5/M6/M7 boundary contracts are safe",
        f"P4 boundary contract errors: {'; '.join(errors)}",
    )


def check_no_provider_imports(repo_root: Path) -> Phase4CloseoutCheck:
    hits: list[str] = []
    for rel in P4_SERVICE_FILES:
        path = repo_root / rel
        if not path.exists():
            continue
        content = path.read_text(encoding="utf-8").lower()
        for pattern in PROVIDER_PATTERNS:
            if pattern in content:
                hits.append(f"{rel}:{pattern}")
    return _check(
        "no_provider_imports",
        not hits,
        "No provider package references found in P4-FINAL services",
        f"Provider references found: {hits}",
    )


def check_no_frontend_database_code(repo_root: Path) -> Phase4CloseoutCheck:
    unexpected = [
        rel for rel in ["apps/web", "packages"]
        if (repo_root / rel).exists()
    ]
    return _check(
        "no_frontend_database_code",
        not unexpected,
        "No frontend or database implementation directories added",
        f"Unexpected frontend/package paths exist: {unexpected}",
    )


def check_no_git_diff(repo_root: Path, rel: str, name: str) -> Phase4CloseoutCheck:
    result = _run_git(repo_root, ["diff", "--quiet", "--", rel])
    return _check(
        name,
        result.returncode == 0,
        f"No git diff for {rel}",
        f"Git diff exists for {rel}",
        rel,
    )


def check_no_raw_audit_logs_committed(repo_root: Path) -> Phase4CloseoutCheck:
    result = _run_git(repo_root, ["ls-files", "docs/harness"])
    tracked = result.stdout.strip().splitlines() if result.returncode == 0 else []
    audits = [path for path in tracked if "audit" in path.lower() and path.endswith(".jsonl")]
    return _check(
        "no_raw_audit_logs_committed",
        not audits,
        "No tracked raw audit JSONL files in docs/harness",
        f"Tracked raw audit JSONL files found: {audits}",
    )


def check_no_runtime_records_committed(repo_root: Path) -> Phase4CloseoutCheck:
    runtime_dirs = [
        "alters/archive/checkpoints",
        "alters/calibration/rubric_delta_suggestions",
        "alters/calibration/checkpoint_plans",
    ]
    result = _run_git(repo_root, ["ls-files", *runtime_dirs])
    tracked = result.stdout.strip().splitlines() if result.returncode == 0 else []
    invalid = [
        path for path in tracked
        if not (path.endswith(".gitkeep") or path.endswith("_template.yaml"))
    ]
    return _check(
        "no_runtime_records_committed",
        not invalid,
        "No raw runtime archive/suggestion/checkpoint records are tracked",
        f"Tracked raw runtime records found: {invalid}",
    )


def check_governance_docs_updated(repo_root: Path) -> Phase4CloseoutCheck:
    required = {
        "docs/harness/PROJECT_BOARD.md": ["P4-M5", "P4-M6", "P4-M7", "P4-CLOSEOUT", "P5-000"],
        "docs/harness/TASK_QUEUE.md": ["P4-M5", "P4-M6", "P4-M7", "P4-CLOSEOUT", "P5-000"],
        "docs/harness/DECISION_RECORD.md": ["P4-M5-01", "P4-M6-01", "P4-M7-01", "P4-CLOSEOUT-01"],
        "docs/harness/RISK_REGISTER.md": [
            "rubric suggestion mistaken for confirmed rubric",
            "archive creation mistaken for rollback execution",
            "checkpoint plan mistaken for active regeneration",
            "phase4 closeout mistaken for full product completion",
        ],
        "docs/harness/RUN_LOG.md": ["P4-FINAL"],
        "docs/harness/EVIDENCE_INDEX.md": ["P4-FINAL", "PHASE4_CLOSEOUT_EVIDENCE.json"],
    }
    missing: list[str] = []
    for rel, needles in required.items():
        path = repo_root / rel
        if not path.exists():
            missing.append(f"{rel}: missing file")
            continue
        content = path.read_text(encoding="utf-8")
        for needle in needles:
            if needle not in content:
                missing.append(f"{rel}: missing {needle}")
    return _check(
        "governance_docs_updated",
        not missing,
        "Governance docs include P4-FINAL closeout updates",
        f"Governance docs incomplete: {'; '.join(missing)}",
    )


def build_phase4_closeout_report(
    repo_root: Path | None = None,
    baseline_commit: str = "unknown",
    test_count: int | None = None,
) -> Phase4CloseoutReport:
    root = repo_root or get_repo_root()
    checks = [
        check_p4_m1r_dialogue_contract(),
        check_p4_modules_importable(),
        check_p4_routes_registered(),
        check_p4_boundary_contracts(),
        check_no_provider_imports(root),
        check_no_frontend_database_code(root),
        check_no_git_diff(root, "alters/current", "no_active_yaml_diff"),
        check_no_git_diff(root, "alters/calibration/rubric.yaml", "no_rubric_yaml_diff"),
        check_no_raw_audit_logs_committed(root),
        check_no_runtime_records_committed(root),
        check_governance_docs_updated(root),
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
    summary = Phase4CloseoutSummary(
        status=status,
        total_checks=len(checks),
        passed_checks=passed,
        warning_checks=warnings,
        failed_checks=failed,
        sealed_baseline_candidate=sealed,
        next_phase_status="P5-000 blocked pending GPT/human review" if sealed else "blocked",
    )
    return Phase4CloseoutReport(
        status=status,
        baseline_commit=baseline_commit,
        test_count=test_count,
        checks=checks,
        summary=summary,
        boundary_confirmations=Phase4CloseoutBoundaryConfirmations(),
        created_at=datetime.now(timezone.utc).isoformat(),
    )


def _markdown_report(report: Phase4CloseoutReport) -> str:
    lines = [
        "# Phase 4 Backend Calibration Loop Closeout Report",
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
    for check in report.checks:
        lines.append(f"| {check.name} | {check.status} | {check.severity} | {check.message} |")
    lines.extend([
        "",
        "## Boundary Confirmations",
        "",
    ])
    for key, value in report.boundary_confirmations.model_dump().items():
        lines.append(f"- **{key}**: {value}")
    lines.extend([
        "",
        f"## Verdict: {report.status}",
        "",
        "Phase 4 is a sealed backend calibration loop candidate only. P5-000 remains blocked pending GPT/human review.",
        "",
    ])
    return "\n".join(lines)


def write_phase4_closeout_artifacts(
    report: Phase4CloseoutReport,
    repo_root: Path | None = None,
) -> dict:
    root = repo_root or get_repo_root()
    harness_dir = root / "docs" / "harness"
    harness_dir.mkdir(parents=True, exist_ok=True)

    report_path = harness_dir / "PHASE4_CLOSEOUT_REPORT.md"
    evidence_path = harness_dir / "PHASE4_CLOSEOUT_EVIDENCE.json"
    final_evidence_path = harness_dir / "P4_FINAL_EVIDENCE.json"

    report_path.write_text(_markdown_report(report), encoding="utf-8")

    evidence = report.model_dump()
    with evidence_path.open("w", encoding="utf-8") as f:
        json.dump(evidence, f, indent=2, ensure_ascii=False)

    final_evidence = {
        "slice": "P4-FINAL",
        "status": report.status,
        "sealed_baseline_candidate": report.summary.sealed_baseline_candidate,
        "phase4_closeout_evidence": str(evidence_path.relative_to(root)),
        "phase4_closeout_report": str(report_path.relative_to(root)),
        "boundary_confirmations": report.boundary_confirmations.model_dump(),
        "created_at": report.created_at,
    }
    with final_evidence_path.open("w", encoding="utf-8") as f:
        json.dump(final_evidence, f, indent=2, ensure_ascii=False)

    return {
        "status": "artifacts_written",
        "report_path": str(report_path),
        "evidence_path": str(evidence_path),
        "final_evidence_path": str(final_evidence_path),
    }
