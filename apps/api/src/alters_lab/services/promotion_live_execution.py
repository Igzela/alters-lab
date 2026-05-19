"""Promotion live execution service."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import yaml

from alters_lab.schemas.promotion_live_execution import (
    LiveExecutionStepResult,
    PromotionLiveExecutionBoundaryConfirmations,
    PromotionLiveExecutionReport,
)
from alters_lab.services.controlled_write import hash_approval_token


def promotion_live_execution_boundary_confirmations(
    active_yaml_modified: bool = False,
    branches_yaml_modified: bool = False,
    alters_modified: bool = False,
    draft_promoted_to_active: bool = False,
) -> dict:
    return PromotionLiveExecutionBoundaryConfirmations(
        active_yaml_modified=active_yaml_modified,
        branches_yaml_modified=branches_yaml_modified,
        alters_modified=alters_modified,
        draft_promoted_to_active=draft_promoted_to_active,
    ).model_dump()


def validate_draft_id(draft_id: str) -> None:
    if not draft_id or not draft_id.strip():
        raise ValueError("draft_id must not be empty")
    if "/" in draft_id or "\\" in draft_id or ".." in draft_id:
        raise ValueError("Invalid draft_id: path traversal detected")


def load_live_execution_inputs(draft_workspace: Path, draft_id: str) -> dict:
    validate_draft_id(draft_id)
    draft_dir = draft_workspace / draft_id

    files = {
        "promotion_package": "promotion_package.yaml",
        "orchestration_plan": "promotion_orchestration_plan.yaml",
        "gate_report": "promotion_execution_gate_report.yaml",
        "execution_packet": "promotion_execution_packet.yaml",
    }

    result: dict = {"paths": {}}
    for key, filename in files.items():
        path = draft_dir / filename
        if not path.exists():
            raise FileNotFoundError(f"Required file not found: {path}")
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if not isinstance(data, dict):
            raise ValueError(f"Invalid format: {filename}")
        result[key] = data
        result["paths"][key] = str(path)

    return result


def validate_gate_for_live_execution(
    package: dict,
    plan: dict,
    gate_report: dict,
    execution_packet: dict,
    final_execution_token: str | None,
    require_matching_gate_token: bool = True,
    require_token: bool = False,
) -> dict:
    errors: list[str] = []

    if gate_report.get("status") != "gate_passed":
        errors.append(f"gate_report.status != 'gate_passed', got '{gate_report.get('status')}'")
    if gate_report.get("gate_passed") is not True:
        errors.append("gate_report.gate_passed != true")

    if execution_packet.get("status") != "execution_packet":
        errors.append(f"execution_packet.status != 'execution_packet', got '{execution_packet.get('status')}'")
    if execution_packet.get("execution_allowed_now") is not False:
        errors.append("execution_packet.execution_allowed_now != false")
    if execution_packet.get("live_execution_allowed_in_p3_m5") is not False:
        errors.append("execution_packet.live_execution_allowed_in_p3_m5 != false")
    if execution_packet.get("requires_p3_m6_live_execution") is not True:
        errors.append("execution_packet.requires_p3_m6_live_execution != true")

    dry_run_results = execution_packet.get("dry_run_results", [])
    for dr in dry_run_results:
        if dr.get("passed") is not True:
            errors.append(f"dry_run {dr.get('target_api')}: not passed")

    ordered_steps = execution_packet.get("ordered_steps", [])
    if not ordered_steps:
        errors.append("execution_packet.ordered_steps is empty")

    pkg_apis = set(package.get("target_persist_apis", []))
    step_apis = set(s.get("target_api") for s in ordered_steps)
    if pkg_apis != step_apis:
        errors.append(f"target_persist_apis mismatch: package={pkg_apis}, packet={step_apis}")

    plan_step_apis = set(s.get("target_api") for s in plan.get("steps", []))
    if plan_step_apis != step_apis:
        errors.append(f"plan steps mismatch: plan={plan_step_apis}, packet={step_apis}")

    has_token = bool(final_execution_token and final_execution_token.strip())
    if require_token and not has_token:
        errors.append("final_execution_token missing")

    if require_matching_gate_token and has_token:
        packet_token_hash = execution_packet.get("final_approval_token_hash")
        if packet_token_hash is None:
            errors.append("execution_packet.final_approval_token_hash is null but require_matching_gate_token=true")
        else:
            provided_hash = hash_approval_token(final_execution_token)
            if provided_hash != packet_token_hash:
                errors.append("final_execution_token hash does not match execution_packet.final_approval_token_hash")

    return {"valid": len(errors) == 0, "errors": errors}


def extract_branches_persist_payload(package: dict) -> dict:
    branches_payload = package.get("branches_payload")
    if not branches_payload:
        raise ValueError("branches_payload missing")

    branch_list = branches_payload.get("branches", [])
    if len(branch_list) != 4:
        raise ValueError(f"branches count != 4, got {len(branch_list)}")

    branch_ids = [b.get("id") for b in branch_list]
    if len(branch_ids) != len(set(branch_ids)):
        raise ValueError("branches contain duplicate IDs")
    if set(branch_ids) != {"branch_A", "branch_B", "branch_C", "branch_D"}:
        raise ValueError(f"branches incomplete: expected branch_A-D, got {set(branch_ids)}")

    for b in branch_list:
        if not b.get("incompatible_with"):
            raise ValueError(f"branch {b.get('id')}: incompatible_with is empty")

    return branches_payload


def extract_alters_persist_payload(package: dict) -> dict:
    alters_payload = package.get("alters_payload")
    if not alters_payload:
        raise ValueError("alters_payload missing")

    alter_list = alters_payload.get("alters", [])
    if len(alter_list) != 4:
        raise ValueError(f"alters count != 4, got {len(alter_list)}")

    alter_ids = [a.get("id") for a in alter_list]
    if len(alter_ids) != len(set(alter_ids)):
        raise ValueError("alters contain duplicate IDs")
    if set(alter_ids) != {"alter_A", "alter_B", "alter_C", "alter_D"}:
        raise ValueError(f"alters incomplete: expected alter_A-D, got {set(alter_ids)}")

    for a in alter_list:
        src = a.get("source_refs", {})
        if src.get("snapshot_ref") != "alters/current/snapshot.yaml":
            raise ValueError(f"alter {a.get('id')}: source_refs.snapshot_ref wrong")
        if src.get("branches_ref") != "alters/current/branches.yaml":
            raise ValueError(f"alter {a.get('id')}: source_refs.branches_ref wrong")
        if src.get("rubric_ref") != "alters/calibration/rubric.yaml":
            raise ValueError(f"alter {a.get('id')}: source_refs.rubric_ref wrong")
        qs = a.get("quality_status", {})
        if qs.get("human_confirmed") is not True:
            raise ValueError(f"alter {a.get('id')}: quality_status.human_confirmed != true")
        if qs.get("active") is not True:
            raise ValueError(f"alter {a.get('id')}: quality_status.active != true")
        voice = a.get("voice", {})
        if not voice.get("core_stance"):
            raise ValueError(f"alter {a.get('id')}: voice.core_stance is empty")

    return alters_payload


def execute_promotion_dry_run(
    package: dict,
    plan: dict,
    path_overrides: dict | None = None,
) -> list[LiveExecutionStepResult]:
    results: list[LiveExecutionStepResult] = []

    steps = plan.get("steps", [])
    for step in steps:
        target_api = step.get("target_api")
        step_id = step.get("step_id")

        if target_api == "/branches/persist":
            try:
                extract_branches_persist_payload(package)
                results.append(LiveExecutionStepResult(
                    step_id=step_id,
                    target_api=target_api,
                    executed=False,
                    dry_run=True,
                    status="dry_run_passed",
                    message="Branches payload satisfies controlled persist contract",
                ))
            except ValueError as e:
                results.append(LiveExecutionStepResult(
                    step_id=step_id,
                    target_api=target_api,
                    executed=False,
                    dry_run=True,
                    status="dry_run_failed",
                    message=str(e),
                ))
        elif target_api == "/alters/persist-batch":
            try:
                extract_alters_persist_payload(package)
                results.append(LiveExecutionStepResult(
                    step_id=step_id,
                    target_api=target_api,
                    executed=False,
                    dry_run=True,
                    status="dry_run_passed",
                    message="Alters payload satisfies controlled persist contract",
                ))
            except ValueError as e:
                results.append(LiveExecutionStepResult(
                    step_id=step_id,
                    target_api=target_api,
                    executed=False,
                    dry_run=True,
                    status="dry_run_failed",
                    message=str(e),
                ))
        else:
            results.append(LiveExecutionStepResult(
                step_id=step_id,
                target_api=target_api,
                executed=False,
                dry_run=True,
                status="dry_run_failed",
                message=f"Unknown target_api: {target_api}",
            ))

    return results


def execute_promotion_live(
    package: dict,
    plan: dict,
    final_execution_token: str,
    path_overrides: dict,
    caller: str = "api",
) -> list[LiveExecutionStepResult]:
    results: list[LiveExecutionStepResult] = []
    branches_succeeded = False

    steps = plan.get("steps", [])
    for step in steps:
        target_api = step.get("target_api")
        step_id = step.get("step_id")

        if target_api == "/branches/persist":
            try:
                branches_payload = extract_branches_persist_payload(package)
                target_path = path_overrides.get("branches_target_path")
                if not target_path:
                    raise ValueError("branches_target_path not provided in path_overrides")

                from alters_lab.schemas.branches import BranchDiscoveryPayload
                from alters_lab.services.branches_persist import write_branches_with_audit
                payload_model = BranchDiscoveryPayload(**branches_payload)
                write_result = write_branches_with_audit(
                    payload=payload_model,
                    target_path=target_path,
                    audit_log_path=path_overrides.get("audit_log_path"),
                    approval_token=final_execution_token,
                    caller=caller,
                    backup_dir=path_overrides.get("backup_dir"),
                )
                branches_succeeded = True
                results.append(LiveExecutionStepResult(
                    step_id=step_id,
                    target_api=target_api,
                    executed=True,
                    dry_run=False,
                    status="executed",
                    target_path=str(target_path),
                    pre_write_hash=write_result.get("pre_write_hash"),
                    post_write_hash=write_result.get("post_write_hash"),
                    backup_path=write_result.get("backup_path"),
                    audit_log_path=write_result.get("audit_log_path"),
                    message="Branches persist executed successfully",
                ))
            except Exception as e:
                results.append(LiveExecutionStepResult(
                    step_id=step_id,
                    target_api=target_api,
                    executed=False,
                    dry_run=False,
                    status="failed",
                    message=str(e),
                ))
                break

        elif target_api == "/alters/persist-batch":
            if not branches_succeeded and any(r.status == "failed" for r in results):
                results.append(LiveExecutionStepResult(
                    step_id=step_id,
                    target_api=target_api,
                    executed=False,
                    dry_run=False,
                    status="skipped",
                    message="Skipped because branches step failed",
                ))
                continue

            try:
                alters_payload = extract_alters_persist_payload(package)
                alters_dir = path_overrides.get("alters_dir")
                if not alters_dir:
                    raise ValueError("alters_dir not provided in path_overrides")

                from alters_lab.schemas.alters import AlterPayload
                from alters_lab.services.alters_persist import write_alter_batch_with_audit
                alters_models = [AlterPayload(**a) for a in alters_payload["alters"]]
                write_result = write_alter_batch_with_audit(
                    alters=alters_models,
                    base_dir=alters_dir,
                    audit_log_path=path_overrides.get("audit_log_path"),
                    approval_token=final_execution_token,
                    caller=caller,
                    backup_dir=path_overrides.get("backup_dir"),
                )
                pre_hashes = write_result.get("pre_write_hashes", {})
                post_hashes = write_result.get("post_write_hashes", {})
                backup_paths_list = write_result.get("backup_paths", [])
                results.append(LiveExecutionStepResult(
                    step_id=step_id,
                    target_api=target_api,
                    executed=True,
                    dry_run=False,
                    status="executed",
                    target_path=str(alters_dir),
                    pre_write_hash=str(pre_hashes) if pre_hashes else None,
                    post_write_hash=str(post_hashes) if post_hashes else None,
                    backup_path=str(backup_paths_list) if backup_paths_list else None,
                    audit_log_path=write_result.get("audit_log_path"),
                    message="Alters batch persist executed successfully",
                ))
            except Exception as e:
                results.append(LiveExecutionStepResult(
                    step_id=step_id,
                    target_api=target_api,
                    executed=False,
                    dry_run=False,
                    status="failed",
                    message=str(e),
                ))

    return results


def build_live_execution_report(
    draft_id: str,
    inputs: dict,
    mode: str,
    final_execution_token: str | None,
    step_results: list[LiveExecutionStepResult],
    validation: dict,
) -> PromotionLiveExecutionReport:
    dry_run_only = mode == "dry_run"
    all_passed = all(r.status in ("dry_run_passed", "executed", "skipped") for r in step_results)
    any_failed = any(r.status in ("dry_run_failed", "failed") for r in step_results)

    if not validation["valid"]:
        status = "rejected"
        live_execution_performed = False
    elif dry_run_only:
        status = "dry_run_passed" if all_passed else "dry_run_failed"
        live_execution_performed = False
    else:
        if any_failed:
            status = "live_failed"
            live_execution_performed = False
        else:
            status = "live_executed"
            live_execution_performed = True

    blocking_failures = validation.get("errors", []) if not validation["valid"] else []

    token_hash = None
    if final_execution_token and final_execution_token.strip():
        token_hash = hash_approval_token(final_execution_token)

    return PromotionLiveExecutionReport(
        draft_id=draft_id,
        status=status,
        live_execution_performed=live_execution_performed,
        dry_run_only=dry_run_only,
        final_execution_token_hash=token_hash,
        source_promotion_package_ref=inputs["paths"]["promotion_package"],
        source_orchestration_plan_ref=inputs["paths"]["orchestration_plan"],
        source_gate_report_ref=inputs["paths"]["gate_report"],
        source_execution_packet_ref=inputs["paths"]["execution_packet"],
        step_results=step_results,
        blocking_failures=blocking_failures,
        boundary_confirmations=PromotionLiveExecutionBoundaryConfirmations(
            branches_yaml_modified=live_execution_performed and any(r.target_api == "/branches/persist" and r.status == "executed" for r in step_results),
            alters_modified=live_execution_performed and any(r.target_api == "/alters/persist-batch" and r.status == "executed" for r in step_results),
        ),
        created_at=datetime.now(timezone.utc).isoformat(),
    )


def run_live_execution_gate(
    draft_workspace: Path,
    draft_id: str,
    request_mode: str,
    final_execution_token: str | None = None,
    require_matching_gate_token: bool = True,
    path_overrides: dict | None = None,
) -> PromotionLiveExecutionReport:
    inputs = load_live_execution_inputs(draft_workspace, draft_id)

    validation = validate_gate_for_live_execution(
        inputs["promotion_package"],
        inputs["orchestration_plan"],
        inputs["gate_report"],
        inputs["execution_packet"],
        final_execution_token,
        require_matching_gate_token,
        require_token=(request_mode == "live"),
    )

    if not validation["valid"]:
        return build_live_execution_report(
            draft_id, inputs, request_mode, final_execution_token, [], validation
        )

    if request_mode == "dry_run":
        step_results = execute_promotion_dry_run(
            inputs["promotion_package"],
            inputs["orchestration_plan"],
            path_overrides,
        )
    else:
        if not path_overrides:
            return build_live_execution_report(
                draft_id, inputs, request_mode, final_execution_token, [],
                {"valid": False, "errors": ["live execution requires path_overrides for safe execution"]},
            )
        step_results = execute_promotion_live(
            inputs["promotion_package"],
            inputs["orchestration_plan"],
            final_execution_token,
            path_overrides,
        )

    return build_live_execution_report(
        draft_id, inputs, request_mode, final_execution_token, step_results, validation
    )


def save_live_execution_report(
    draft_workspace: Path,
    draft_id: str,
    report: PromotionLiveExecutionReport,
    final_execution_token: str,
    caller: str = "api",
) -> dict:
    if not final_execution_token or not final_execution_token.strip():
        raise ValueError("final_execution_token must not be empty or whitespace-only")

    draft_dir = draft_workspace / draft_id
    draft_dir.mkdir(parents=True, exist_ok=True)
    report_path = draft_dir / "promotion_live_execution_report.yaml"

    content = yaml.dump(report.model_dump(), default_flow_style=False, allow_unicode=True)
    report_path.write_text(content, encoding="utf-8")

    return {
        "status": "report_saved",
        "report_path": str(report_path),
        "approval_token_hash": hash_approval_token(final_execution_token),
    }


def list_live_execution_reports(draft_workspace: Path) -> list[dict]:
    if not draft_workspace.exists():
        return []
    reports = []
    for d in sorted(draft_workspace.iterdir()):
        if d.is_dir() and d.name.startswith("draft_"):
            report_path = d / "promotion_live_execution_report.yaml"
            reports.append({
                "draft_id": d.name,
                "live_execution_report_exists": report_path.exists(),
                "live_execution_report_path": str(report_path),
            })
    return reports
