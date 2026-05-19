"""Promotion execution gate service."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import yaml

from alters_lab.schemas.promotion_execution_gate import (
    DryRunCheckResult,
    ExecutionPacket,
    ExecutionPrerequisiteCheck,
    PromotionExecutionGateBoundaryConfirmations,
    PromotionExecutionGateReport,
)
from alters_lab.services.controlled_write import hash_approval_token


def promotion_execution_gate_boundary_confirmations() -> dict:
    return PromotionExecutionGateBoundaryConfirmations().model_dump()


def validate_draft_id(draft_id: str) -> None:
    if not draft_id or not draft_id.strip():
        raise ValueError("draft_id must not be empty")
    if "/" in draft_id or "\\" in draft_id or ".." in draft_id:
        raise ValueError("Invalid draft_id: path traversal detected")


def load_gate_inputs(draft_workspace: Path, draft_id: str) -> dict:
    validate_draft_id(draft_id)
    draft_dir = draft_workspace / draft_id

    pkg_path = draft_dir / "promotion_package.yaml"
    if not pkg_path.exists():
        raise FileNotFoundError(f"Promotion package not found: {pkg_path}")

    plan_path = draft_dir / "promotion_orchestration_plan.yaml"
    if not plan_path.exists():
        raise FileNotFoundError(f"Orchestration plan not found: {plan_path}")

    with open(pkg_path, encoding="utf-8") as f:
        package = yaml.safe_load(f)
    with open(plan_path, encoding="utf-8") as f:
        plan = yaml.safe_load(f)

    if not isinstance(package, dict):
        raise ValueError("Invalid promotion package format")
    if not isinstance(plan, dict):
        raise ValueError("Invalid orchestration plan format")

    return {
        "promotion_package": package,
        "orchestration_plan": plan,
        "promotion_package_path": str(pkg_path),
        "orchestration_plan_path": str(plan_path),
    }


def validate_orchestration_plan_for_execution_gate(plan: dict) -> dict:
    errors: list[str] = []

    if plan.get("status") != "promotion_plan":
        errors.append(f"status != 'promotion_plan', got '{plan.get('status')}'")
    if plan.get("active_execution_allowed") is not False:
        errors.append("active_execution_allowed != false")
    if plan.get("requires_human_final_approval") is not True:
        errors.append("requires_human_final_approval != true")

    steps = plan.get("steps", [])
    if not steps:
        errors.append("steps is empty")

    ALLOWED_APIS = {"/branches/persist", "/alters/persist-batch"}
    for step in steps:
        if step.get("execution_allowed_in_p3_m4") is not False:
            errors.append(f"step {step.get('step_id')}: execution_allowed_in_p3_m4 != false")
        if step.get("requires_human_approval") is not True:
            errors.append(f"step {step.get('step_id')}: requires_human_approval != true")
        if step.get("target_api") not in ALLOWED_APIS:
            errors.append(f"step {step.get('step_id')}: target_api '{step.get('target_api')}' not in allowed")

    evidence = plan.get("evidence_required", [])
    if not evidence:
        errors.append("evidence_required is empty")

    bc = plan.get("boundary_confirmations", {})
    if bc.get("controlled_persist_api_called") is not False:
        errors.append("boundary_confirmations.controlled_persist_api_called != false")

    return {"valid": len(errors) == 0, "errors": errors}


def validate_promotion_package_for_execution_gate(package: dict) -> dict:
    errors: list[str] = []

    if package.get("status") != "promotion_candidate":
        errors.append(f"status != 'promotion_candidate', got '{package.get('status')}'")
    if package.get("active_write_allowed") is not False:
        errors.append("active_write_allowed != false")
    if package.get("requires_controlled_persist_api") is not True:
        errors.append("requires_controlled_persist_api != true")

    target_apis = package.get("target_persist_apis", [])
    ALLOWED_APIS = {"/branches/persist", "/alters/persist-batch"}
    for api in target_apis:
        if api not in ALLOWED_APIS:
            errors.append(f"target_persist_api '{api}' not in allowed: {ALLOWED_APIS}")

    branches_payload = package.get("branches_payload")
    if branches_payload:
        branch_list = branches_payload.get("branches", [])
        if len(branch_list) != 4:
            errors.append(f"branches count != 4, got {len(branch_list)}")
        branch_ids = [b.get("id") for b in branch_list]
        if len(branch_ids) != len(set(branch_ids)):
            errors.append("branches contain duplicate IDs")
        if set(branch_ids) != {"branch_A", "branch_B", "branch_C", "branch_D"}:
            errors.append(f"branches incomplete: expected branch_A-D, got {set(branch_ids)}")

    alters_payload = package.get("alters_payload")
    if alters_payload:
        alter_list = alters_payload.get("alters", [])
        if len(alter_list) != 4:
            errors.append(f"alters count != 4, got {len(alter_list)}")
        alter_ids = [a.get("id") for a in alter_list]
        if len(alter_ids) != len(set(alter_ids)):
            errors.append("alters contain duplicate IDs")
        if set(alter_ids) != {"alter_A", "alter_B", "alter_C", "alter_D"}:
            errors.append(f"alters incomplete: expected alter_A-D, got {set(alter_ids)}")
        for a in alter_list:
            src = a.get("source_refs", {})
            if src.get("snapshot_ref") != "alters/current/snapshot.yaml":
                errors.append(f"alter {a.get('id')}: source_refs.snapshot_ref wrong")
            if src.get("branches_ref") != "alters/current/branches.yaml":
                errors.append(f"alter {a.get('id')}: source_refs.branches_ref wrong")
            if src.get("rubric_ref") != "alters/calibration/rubric.yaml":
                errors.append(f"alter {a.get('id')}: source_refs.rubric_ref wrong")
            qs = a.get("quality_status", {})
            if qs.get("human_confirmed") is not True:
                errors.append(f"alter {a.get('id')}: quality_status.human_confirmed != true")
            if qs.get("active") is not True:
                errors.append(f"alter {a.get('id')}: quality_status.active != true")

    return {"valid": len(errors) == 0, "errors": errors}


def compare_package_and_plan(package: dict, plan: dict) -> dict:
    errors: list[str] = []

    pkg_apis = set(package.get("target_persist_apis", []))
    step_apis = set(s.get("target_api") for s in plan.get("steps", []))
    if pkg_apis != step_apis:
        errors.append(f"target_persist_apis mismatch: package={pkg_apis}, plan={step_apis}")

    branches_payload = package.get("branches_payload")
    has_branches_step = "/branches/persist" in step_apis
    if branches_payload and not has_branches_step:
        errors.append("package has branches_payload but plan has no /branches/persist step")

    alters_payload = package.get("alters_payload")
    has_alters_step = "/alters/persist-batch" in step_apis
    if alters_payload and not has_alters_step:
        errors.append("package has alters_payload but plan has no /alters/persist-batch step")

    steps = plan.get("steps", [])
    if len(steps) == 2:
        if steps[0].get("target_api") != "/branches/persist":
            errors.append("step ordering: /branches/persist must come before /alters/persist-batch")

    source_ref = plan.get("source_promotion_package_ref", "")
    if not source_ref.endswith("promotion_package.yaml"):
        errors.append(f"source_promotion_package_ref does not end with promotion_package.yaml: {source_ref}")

    if package.get("draft_id") and plan.get("draft_id"):
        if package["draft_id"] != plan["draft_id"]:
            errors.append(f"draft_id mismatch: package={package['draft_id']}, plan={plan['draft_id']}")

    return {"valid": len(errors) == 0, "errors": errors}


def build_prerequisite_checks(
    package: dict,
    plan: dict,
    final_approval_token: str | None,
) -> list[ExecutionPrerequisiteCheck]:
    checks: list[ExecutionPrerequisiteCheck] = []

    pkg_val = validate_promotion_package_for_execution_gate(package)
    checks.append(ExecutionPrerequisiteCheck(
        name="promotion_package_valid",
        passed=pkg_val["valid"],
        severity="blocking",
        message="Promotion package validation passed" if pkg_val["valid"] else f"Errors: {'; '.join(pkg_val['errors'])}",
    ))

    plan_val = validate_orchestration_plan_for_execution_gate(plan)
    checks.append(ExecutionPrerequisiteCheck(
        name="orchestration_plan_valid",
        passed=plan_val["valid"],
        severity="blocking",
        message="Orchestration plan validation passed" if plan_val["valid"] else f"Errors: {'; '.join(plan_val['errors'])}",
    ))

    cmp_val = compare_package_and_plan(package, plan)
    checks.append(ExecutionPrerequisiteCheck(
        name="package_plan_consistency",
        passed=cmp_val["valid"],
        severity="blocking",
        message="Package-plan consistency passed" if cmp_val["valid"] else f"Errors: {'; '.join(cmp_val['errors'])}",
    ))

    has_token = bool(final_approval_token and final_approval_token.strip())
    checks.append(ExecutionPrerequisiteCheck(
        name="final_approval_token_present",
        passed=has_token,
        severity="blocking",
        message="Final approval token present" if has_token else "Final approval token missing",
    ))

    checks.append(ExecutionPrerequisiteCheck(
        name="dry_run_required_before_live",
        passed=True,
        severity="info",
        message="Dry-run is required before live execution",
    ))

    checks.append(ExecutionPrerequisiteCheck(
        name="p3_m5_live_execution_disabled",
        passed=True,
        severity="info",
        message="P3-M5 live execution is disabled",
    ))

    checks.append(ExecutionPrerequisiteCheck(
        name="p3_m6_required_for_live",
        passed=True,
        severity="info",
        message="P3-M6 is required for live execution",
    ))

    evidence = plan.get("evidence_required", [])
    checks.append(ExecutionPrerequisiteCheck(
        name="evidence_requirements_present",
        passed=bool(evidence),
        severity="blocking" if not evidence else "info",
        message=f"{len(evidence)} evidence requirements defined" if evidence else "No evidence requirements",
    ))

    return checks


def run_dry_run_compatibility_checks(package: dict) -> list[DryRunCheckResult]:
    results: list[DryRunCheckResult] = []

    branches_payload = package.get("branches_payload")
    if branches_payload:
        branch_list = branches_payload.get("branches", [])
        branch_ids = [b.get("id") for b in branch_list]
        valid = (
            len(branch_list) == 4
            and len(branch_ids) == len(set(branch_ids))
            and set(branch_ids) == {"branch_A", "branch_B", "branch_C", "branch_D"}
            and all(b.get("incompatible_with") for b in branch_list)
        )
        results.append(DryRunCheckResult(
            target_api="/branches/persist",
            attempted=True,
            passed=valid,
            dry_run_only=True,
            payload_ref="promotion_package.branches_payload",
            message="Branches payload satisfies controlled branches persist contract" if valid else "Branches payload fails contract validation",
            expected_artifact="alters/current/branches.yaml",
        ))

    alters_payload = package.get("alters_payload")
    if alters_payload:
        alter_list = alters_payload.get("alters", [])
        alter_ids = [a.get("id") for a in alter_list]
        valid_alter_ids = (
            len(alter_list) == 4
            and len(alter_ids) == len(set(alter_ids))
            and set(alter_ids) == {"alter_A", "alter_B", "alter_C", "alter_D"}
        )
        valid_source_refs = all(
            a.get("source_refs", {}).get("snapshot_ref") == "alters/current/snapshot.yaml"
            and a.get("source_refs", {}).get("branches_ref") == "alters/current/branches.yaml"
            and a.get("source_refs", {}).get("rubric_ref") == "alters/calibration/rubric.yaml"
            for a in alter_list
        )
        valid_quality = all(
            a.get("quality_status", {}).get("human_confirmed") is True
            and a.get("quality_status", {}).get("active") is True
            for a in alter_list
        )
        valid = valid_alter_ids and valid_source_refs and valid_quality
        results.append(DryRunCheckResult(
            target_api="/alters/persist-batch",
            attempted=True,
            passed=valid,
            dry_run_only=True,
            payload_ref="promotion_package.alters_payload",
            message="Alters payload satisfies controlled alters batch persist contract" if valid else "Alters payload fails contract validation",
            expected_artifact="alters/current/alters/alter_A-D.yaml",
        ))

    return results


def build_execution_packet(
    draft_id: str,
    package: dict,
    plan: dict,
    dry_run_results: list[DryRunCheckResult],
    prerequisites: list[ExecutionPrerequisiteCheck],
    final_approval_token: str | None,
) -> ExecutionPacket:
    token_hash = None
    if final_approval_token and final_approval_token.strip():
        token_hash = hash_approval_token(final_approval_token)

    return ExecutionPacket(
        draft_id=draft_id,
        final_approval_token_hash=token_hash,
        source_promotion_package_ref=f"{draft_id}/promotion_package.yaml",
        source_orchestration_plan_ref=f"{draft_id}/promotion_orchestration_plan.yaml",
        ordered_steps=plan.get("steps", []),
        dry_run_results=dry_run_results,
        prerequisites=prerequisites,
        evidence_required=plan.get("evidence_required", []),
        boundary_confirmations=PromotionExecutionGateBoundaryConfirmations(),
        created_at=datetime.now(timezone.utc).isoformat(),
    )


def build_gate_report(
    draft_id: str,
    package: dict,
    plan: dict,
    run_dry_run: bool,
    final_approval_token: str | None,
) -> PromotionExecutionGateReport:
    prerequisites = build_prerequisite_checks(package, plan, final_approval_token)
    dry_run_results = run_dry_run_compatibility_checks(package) if run_dry_run else []

    blocking_failures = [
        p.name for p in prerequisites if not p.passed and p.severity == "blocking"
    ]
    warnings = [
        p.name for p in prerequisites if not p.passed and p.severity == "warning"
    ]

    if run_dry_run:
        failed_dry_runs = [dr.target_api for dr in dry_run_results if not dr.passed]
        if failed_dry_runs:
            blocking_failures.extend([f"dry_run_failed_{api}" for api in failed_dry_runs])

    gate_passed = len(blocking_failures) == 0

    packet = None
    if gate_passed:
        packet = build_execution_packet(
            draft_id, package, plan, dry_run_results, prerequisites, final_approval_token
        )

    return PromotionExecutionGateReport(
        draft_id=draft_id,
        status="gate_passed" if gate_passed else "gate_failed",
        gate_passed=gate_passed,
        blocking_failures=blocking_failures,
        warnings=warnings,
        execution_packet=packet,
        boundary_confirmations=PromotionExecutionGateBoundaryConfirmations(),
        created_at=datetime.now(timezone.utc).isoformat(),
    )


def save_gate_report(
    draft_workspace: Path,
    draft_id: str,
    report: PromotionExecutionGateReport,
    final_approval_token: str,
    caller: str = "api",
) -> dict:
    if not final_approval_token or not final_approval_token.strip():
        raise ValueError("final_approval_token must not be empty or whitespace-only")

    draft_dir = draft_workspace / draft_id
    draft_dir.mkdir(parents=True, exist_ok=True)

    report_path = draft_dir / "promotion_execution_gate_report.yaml"
    content = yaml.dump(report.model_dump(), default_flow_style=False, allow_unicode=True)
    report_path.write_text(content, encoding="utf-8")

    packet_path = None
    if report.execution_packet:
        packet_path_obj = draft_dir / "promotion_execution_packet.yaml"
        packet_content = yaml.dump(
            report.execution_packet.model_dump(),
            default_flow_style=False,
            allow_unicode=True,
        )
        packet_path_obj.write_text(packet_content, encoding="utf-8")
        packet_path = str(packet_path_obj)

    return {
        "status": "report_saved",
        "report_path": str(report_path),
        "packet_path": packet_path,
        "approval_token_hash": hash_approval_token(final_approval_token),
    }


def list_execution_gate_reports(draft_workspace: Path) -> list[dict]:
    if not draft_workspace.exists():
        return []
    reports = []
    for d in sorted(draft_workspace.iterdir()):
        if d.is_dir() and d.name.startswith("draft_"):
            report_path = d / "promotion_execution_gate_report.yaml"
            packet_path = d / "promotion_execution_packet.yaml"
            reports.append({
                "draft_id": d.name,
                "report_exists": report_path.exists(),
                "packet_exists": packet_path.exists(),
                "report_path": str(report_path),
                "packet_path": str(packet_path),
            })
    return reports
