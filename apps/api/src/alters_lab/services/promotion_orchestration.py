"""Promotion orchestration plan service."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import yaml

from alters_lab.schemas.promotion_orchestration import (
    PromotionEvidenceRequirement,
    PromotionOrchestrationBoundaryConfirmations,
    PromotionOrchestrationPlan,
    PromotionPlanStep,
    PromotionRollbackPlan,
)
from alters_lab.services.controlled_write import hash_approval_token


def promotion_orchestration_boundary_confirmations() -> dict:
    return PromotionOrchestrationBoundaryConfirmations().model_dump()


def validate_draft_id(draft_id: str) -> None:
    if not draft_id or not draft_id.strip():
        raise ValueError("draft_id must not be empty")
    if "/" in draft_id or "\\" in draft_id or ".." in draft_id:
        raise ValueError("Invalid draft_id: path traversal detected")


def load_promotion_package(draft_workspace: Path, draft_id: str) -> dict:
    validate_draft_id(draft_id)
    pkg_path = draft_workspace / draft_id / "promotion_package.yaml"
    if not pkg_path.exists():
        raise FileNotFoundError(f"Promotion package not found: {pkg_path}")
    with open(pkg_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError("Invalid promotion package format")
    return data


def validate_promotion_package_for_orchestration(package: dict) -> dict:
    errors: list[str] = []

    if package.get("status") != "promotion_candidate":
        errors.append(f"status != 'promotion_candidate', got '{package.get('status')}'")
    if package.get("active_write_allowed") is not False:
        errors.append("active_write_allowed != false")
    if package.get("requires_controlled_persist_api") is not True:
        errors.append("requires_controlled_persist_api != true")

    target_apis = package.get("target_persist_apis", [])
    if not target_apis:
        errors.append("target_persist_apis is empty")

    ALLOWED_APIS = {"/branches/persist", "/alters/persist-batch"}
    for api in target_apis:
        if api not in ALLOWED_APIS:
            errors.append(f"target_persist_api '{api}' not in allowed: {ALLOWED_APIS}")

    branches_payload = package.get("branches_payload")
    alters_payload = package.get("alters_payload")

    if "/branches/persist" in target_apis:
        if not branches_payload:
            errors.append("branches_payload missing when /branches/persist targeted")
        else:
            branch_list = branches_payload.get("branches", [])
            if len(branch_list) != 4:
                errors.append(f"branches count != 4, got {len(branch_list)}")
            branch_ids = [b.get("id") for b in branch_list]
            if len(branch_ids) != len(set(branch_ids)):
                errors.append("branches contain duplicate IDs")
            if set(branch_ids) != {"branch_A", "branch_B", "branch_C", "branch_D"}:
                errors.append(f"branches incomplete: expected branch_A-D, got {set(branch_ids)}")

    if "/alters/persist-batch" in target_apis:
        if not alters_payload:
            errors.append("alters_payload missing when /alters/persist-batch targeted")
        else:
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

    bc = package.get("boundary_confirmations", {})
    if bc.get("active_write_allowed") is not False:
        errors.append("boundary_confirmations.active_write_allowed != false")

    return {"valid": len(errors) == 0, "errors": errors}


def build_promotion_steps(package: dict) -> list[PromotionPlanStep]:
    steps: list[PromotionPlanStep] = []
    target_apis = package.get("target_persist_apis", [])

    if "/branches/persist" in target_apis:
        steps.append(PromotionPlanStep(
            step_id="step_01_branches_persist",
            target_api="/branches/persist",
            payload_ref="promotion_package.branches_payload",
            purpose="Persist reviewed branches payload through controlled write API",
            execution_allowed_in_p3_m4=False,
            expected_artifact="alters/current/branches.yaml",
            rollback_note="Use controlled write backup/audit from branches persist execution",
        ))

    if "/alters/persist-batch" in target_apis:
        steps.append(PromotionPlanStep(
            step_id="step_02_alters_persist_batch",
            target_api="/alters/persist-batch",
            payload_ref="promotion_package.alters_payload",
            purpose="Persist reviewed alter payloads through controlled write API",
            execution_allowed_in_p3_m4=False,
            expected_artifact="alters/current/alters/alter_A-D.yaml",
            rollback_note="Use controlled write backup/audit from alters persist execution",
        ))

    return steps


def build_evidence_requirements(package: dict) -> list[PromotionEvidenceRequirement]:
    reqs = [
        PromotionEvidenceRequirement(
            name="human_final_approval_token",
            required=True,
            description="Human final approval token required before execution",
        ),
    ]

    target_apis = package.get("target_persist_apis", [])
    if "/branches/persist" in target_apis:
        reqs.append(PromotionEvidenceRequirement(
            name="dry_run_branches_persist",
            required=True,
            description="Dry-run response from /branches/persist before live execution",
        ))
    if "/alters/persist-batch" in target_apis:
        reqs.append(PromotionEvidenceRequirement(
            name="dry_run_alters_persist_batch",
            required=True,
            description="Dry-run response from /alters/persist-batch before live execution",
        ))

    reqs.extend([
        PromotionEvidenceRequirement(
            name="active_yaml_diff_check",
            required=True,
            description="Active YAML diff check after execution",
        ),
        PromotionEvidenceRequirement(
            name="audit_log_verification",
            required=True,
            description="Audit log verification after execution",
        ),
        PromotionEvidenceRequirement(
            name="validation_after_execution",
            required=True,
            description="Tests or validation after execution",
        ),
        PromotionEvidenceRequirement(
            name="rollback_backup_path_verification",
            required=True,
            description="Rollback backup path verification",
        ),
    ])

    return reqs


def build_rollback_plan(package: dict) -> PromotionRollbackPlan:
    required_backups = []
    target_apis = package.get("target_persist_apis", [])
    if "/branches/persist" in target_apis:
        required_backups.append("alters/current/branches.yaml")
    if "/alters/persist-batch" in target_apis:
        required_backups.append("alters/current/alters/alter_A-D.yaml")

    return PromotionRollbackPlan(
        rollback_available=True,
        notes=[
            "P3-M4 does not create backups",
            "Backups are created only by controlled persist execution",
            "Each controlled persist API creates backup before writing",
        ],
        required_backups=required_backups,
    )


def build_orchestration_plan(
    draft_workspace: Path,
    draft_id: str,
) -> PromotionOrchestrationPlan:
    package = load_promotion_package(draft_workspace, draft_id)
    validation = validate_promotion_package_for_orchestration(package)
    if not validation["valid"]:
        raise ValueError(f"Invalid promotion package: {'; '.join(validation['errors'])}")

    steps = build_promotion_steps(package)
    evidence = build_evidence_requirements(package)
    rollback = build_rollback_plan(package)

    return PromotionOrchestrationPlan(
        draft_id=draft_id,
        source_promotion_package_ref=f"{draft_id}/promotion_package.yaml",
        steps=steps,
        evidence_required=evidence,
        rollback_plan=rollback,
        boundary_confirmations=PromotionOrchestrationBoundaryConfirmations(),
        created_at=datetime.now(timezone.utc).isoformat(),
    )


def save_orchestration_plan(
    draft_workspace: Path,
    draft_id: str,
    plan: PromotionOrchestrationPlan,
    approval_token: str,
    caller: str = "api",
) -> dict:
    if not approval_token or not approval_token.strip():
        raise ValueError("approval_token must not be empty or whitespace-only")

    draft_dir = draft_workspace / draft_id
    draft_dir.mkdir(parents=True, exist_ok=True)
    plan_path = draft_dir / "promotion_orchestration_plan.yaml"

    content = yaml.dump(plan.model_dump(), default_flow_style=False, allow_unicode=True)
    plan_path.write_text(content, encoding="utf-8")

    return {
        "status": "plan_saved",
        "plan_path": str(plan_path),
        "approval_token_hash": hash_approval_token(approval_token),
    }


def list_orchestration_plans(draft_workspace: Path) -> list[dict]:
    if not draft_workspace.exists():
        return []
    plans = []
    for d in sorted(draft_workspace.iterdir()):
        if d.is_dir() and d.name.startswith("draft_"):
            plan_path = d / "promotion_orchestration_plan.yaml"
            plans.append({
                "draft_id": d.name,
                "plan_exists": plan_path.exists(),
                "plan_path": str(plan_path),
            })
    return plans
