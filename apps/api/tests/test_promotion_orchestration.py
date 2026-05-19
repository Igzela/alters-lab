"""Service tests for promotion orchestration plan."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from alters_lab.schemas.promotion_orchestration import (
    PromotionOrchestrationBoundaryConfirmations,
    PromotionOrchestrationPlan,
    PromotionOrchestrationRequest,
    PromotionPlanStep,
)
from alters_lab.services.promotion_orchestration import (
    build_evidence_requirements,
    build_orchestration_plan,
    build_promotion_steps,
    build_rollback_plan,
    list_orchestration_plans,
    load_promotion_package,
    promotion_orchestration_boundary_confirmations,
    save_orchestration_plan,
    validate_draft_id,
    validate_promotion_package_for_orchestration,
)


def _valid_promotion_package() -> dict:
    return {
        "draft_id": "draft_test_001",
        "schema_version": 1,
        "status": "promotion_candidate",
        "active_write_allowed": False,
        "requires_controlled_persist_api": True,
        "target_persist_apis": ["/branches/persist", "/alters/persist-batch"],
        "review_decision": {
            "draft_id": "draft_test_001",
            "decision": "approve_for_promotion_package",
            "approved_branch_ids": ["branch_A", "branch_B", "branch_C", "branch_D"],
            "approved_alter_ids": ["alter_A", "alter_B", "alter_C", "alter_D"],
            "boundary_confirmations": {"draft_only": True, "active_yaml_modified": False},
        },
        "branches_payload": {
            "branch_discovery": {"status": "completed"},
            "branches": [
                {"id": f"branch_{c}", "label": f"Branch {c}"}
                for c in "ABCD"
            ],
        },
        "alters_payload": {
            "alters": [
                {
                    "id": f"alter_{c}",
                    "branch_ref": f"branch_{c}",
                    "label": f"Alter {c}",
                    "source_refs": {
                        "snapshot_ref": "alters/current/snapshot.yaml",
                        "branches_ref": "alters/current/branches.yaml",
                        "rubric_ref": "alters/calibration/rubric.yaml",
                    },
                    "quality_status": {"human_confirmed": True, "active": True},
                    "voice": {"core_stance": "focused"},
                }
                for c in "ABCD"
            ],
        },
        "boundary_confirmations": {"active_write_allowed": False},
    }


def _write_promotion_package(workspace: Path, draft_id: str, pkg: dict):
    d = workspace / draft_id
    d.mkdir(parents=True, exist_ok=True)
    (d / "promotion_package.yaml").write_text(yaml.dump(pkg), encoding="utf-8")


# --- boundary confirmations ---


def test_boundary_confirmations_all_false():
    bc = promotion_orchestration_boundary_confirmations()
    assert bc["plan_only"] is True
    assert bc["active_yaml_modified"] is False
    assert bc["controlled_persist_api_called"] is False
    assert bc["draft_promoted_to_active"] is False
    assert bc["provider_used"] is False


# --- validate_draft_id ---


def test_validate_draft_id_rejects_empty():
    with pytest.raises(ValueError, match="empty"):
        validate_draft_id("")


def test_validate_draft_id_rejects_slash():
    with pytest.raises(ValueError, match="path traversal"):
        validate_draft_id("draft/evil")


def test_validate_draft_id_rejects_backslash():
    with pytest.raises(ValueError, match="path traversal"):
        validate_draft_id("draft\\..\\secret")


def test_validate_draft_id_rejects_dotdot():
    with pytest.raises(ValueError, match="path traversal"):
        validate_draft_id("../../../etc")


# --- load_promotion_package ---


def test_load_promotion_package(tmp_path):
    _write_promotion_package(tmp_path, "draft_001", _valid_promotion_package())
    pkg = load_promotion_package(tmp_path, "draft_001")
    assert pkg["draft_id"] == "draft_test_001"
    assert pkg["status"] == "promotion_candidate"


def test_load_promotion_package_rejects_missing(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_promotion_package(tmp_path, "nonexistent")


def test_load_promotion_package_rejects_path_traversal(tmp_path):
    with pytest.raises(ValueError, match="path traversal"):
        load_promotion_package(tmp_path, "../etc/passwd")


# --- validate_promotion_package_for_orchestration ---


def test_validate_passes_valid():
    result = validate_promotion_package_for_orchestration(_valid_promotion_package())
    assert result["valid"] is True
    assert result["errors"] == []


def test_validate_rejects_active_write_allowed():
    pkg = _valid_promotion_package()
    pkg["active_write_allowed"] = True
    result = validate_promotion_package_for_orchestration(pkg)
    assert result["valid"] is False
    assert any("active_write_allowed" in e for e in result["errors"])


def test_validate_rejects_requires_controlled_persist_api_false():
    pkg = _valid_promotion_package()
    pkg["requires_controlled_persist_api"] = False
    result = validate_promotion_package_for_orchestration(pkg)
    assert result["valid"] is False
    assert any("requires_controlled_persist_api" in e for e in result["errors"])


def test_validate_rejects_invalid_target_api():
    pkg = _valid_promotion_package()
    pkg["target_persist_apis"] = ["/evil/persist"]
    result = validate_promotion_package_for_orchestration(pkg)
    assert result["valid"] is False
    assert any("not in allowed" in e for e in result["errors"])


def test_validate_rejects_missing_branches_payload():
    pkg = _valid_promotion_package()
    pkg["branches_payload"] = None
    result = validate_promotion_package_for_orchestration(pkg)
    assert result["valid"] is False
    assert any("branches_payload missing" in e for e in result["errors"])


def test_validate_rejects_missing_alters_payload():
    pkg = _valid_promotion_package()
    pkg["alters_payload"] = None
    result = validate_promotion_package_for_orchestration(pkg)
    assert result["valid"] is False
    assert any("alters_payload missing" in e for e in result["errors"])


def test_validate_rejects_branches_not_exactly_ad():
    pkg = _valid_promotion_package()
    pkg["branches_payload"]["branches"] = [
        {"id": "branch_A", "label": "A"},
        {"id": "branch_B", "label": "B"},
    ]
    result = validate_promotion_package_for_orchestration(pkg)
    assert result["valid"] is False
    assert any("branches count != 4" in e for e in result["errors"])


def test_validate_rejects_duplicate_branch_ids():
    pkg = _valid_promotion_package()
    pkg["branches_payload"]["branches"] = [
        {"id": "branch_A", "label": "A"},
        {"id": "branch_A", "label": "A2"},
        {"id": "branch_C", "label": "C"},
        {"id": "branch_D", "label": "D"},
    ]
    result = validate_promotion_package_for_orchestration(pkg)
    assert result["valid"] is False
    assert any("duplicate" in e for e in result["errors"])


def test_validate_rejects_alters_not_exactly_ad():
    pkg = _valid_promotion_package()
    pkg["alters_payload"]["alters"] = [
        {"id": "alter_A", "branch_ref": "branch_A", "label": "A",
         "source_refs": {"snapshot_ref": "alters/current/snapshot.yaml", "branches_ref": "alters/current/branches.yaml", "rubric_ref": "alters/calibration/rubric.yaml"},
         "quality_status": {"human_confirmed": True, "active": True}, "voice": {"core_stance": "x"}},
    ]
    result = validate_promotion_package_for_orchestration(pkg)
    assert result["valid"] is False
    assert any("alters count != 4" in e for e in result["errors"])


def test_validate_rejects_duplicate_alter_ids():
    pkg = _valid_promotion_package()
    pkg["alters_payload"]["alters"] = [
        {"id": "alter_A", "branch_ref": "branch_A", "label": "A",
         "source_refs": {"snapshot_ref": "alters/current/snapshot.yaml", "branches_ref": "alters/current/branches.yaml", "rubric_ref": "alters/calibration/rubric.yaml"},
         "quality_status": {"human_confirmed": True, "active": True}, "voice": {"core_stance": "x"}},
        {"id": "alter_A", "branch_ref": "branch_A", "label": "A2",
         "source_refs": {"snapshot_ref": "alters/current/snapshot.yaml", "branches_ref": "alters/current/branches.yaml", "rubric_ref": "alters/calibration/rubric.yaml"},
         "quality_status": {"human_confirmed": True, "active": True}, "voice": {"core_stance": "x"}},
        {"id": "alter_C", "branch_ref": "branch_C", "label": "C",
         "source_refs": {"snapshot_ref": "alters/current/snapshot.yaml", "branches_ref": "alters/current/branches.yaml", "rubric_ref": "alters/calibration/rubric.yaml"},
         "quality_status": {"human_confirmed": True, "active": True}, "voice": {"core_stance": "x"}},
        {"id": "alter_D", "branch_ref": "branch_D", "label": "D",
         "source_refs": {"snapshot_ref": "alters/current/snapshot.yaml", "branches_ref": "alters/current/branches.yaml", "rubric_ref": "alters/calibration/rubric.yaml"},
         "quality_status": {"human_confirmed": True, "active": True}, "voice": {"core_stance": "x"}},
    ]
    result = validate_promotion_package_for_orchestration(pkg)
    assert result["valid"] is False
    assert any("duplicate" in e for e in result["errors"])


def test_validate_rejects_bad_alter_source_refs():
    pkg = _valid_promotion_package()
    pkg["alters_payload"]["alters"][0]["source_refs"]["snapshot_ref"] = "wrong"
    result = validate_promotion_package_for_orchestration(pkg)
    assert result["valid"] is False
    assert any("source_refs" in e for e in result["errors"])


def test_validate_rejects_alter_human_confirmed_false():
    pkg = _valid_promotion_package()
    pkg["alters_payload"]["alters"][0]["quality_status"]["human_confirmed"] = False
    result = validate_promotion_package_for_orchestration(pkg)
    assert result["valid"] is False
    assert any("human_confirmed" in e for e in result["errors"])


def test_validate_rejects_alter_active_false():
    pkg = _valid_promotion_package()
    pkg["alters_payload"]["alters"][0]["quality_status"]["active"] = False
    result = validate_promotion_package_for_orchestration(pkg)
    assert result["valid"] is False
    assert any("active" in e for e in result["errors"])


def test_validate_rejects_status_wrong():
    pkg = _valid_promotion_package()
    pkg["status"] = "draft"
    result = validate_promotion_package_for_orchestration(pkg)
    assert result["valid"] is False
    assert any("status" in e for e in result["errors"])


def test_validate_rejects_empty_target_apis():
    pkg = _valid_promotion_package()
    pkg["target_persist_apis"] = []
    result = validate_promotion_package_for_orchestration(pkg)
    assert result["valid"] is False
    assert any("empty" in e for e in result["errors"])


def test_validate_rejects_boundary_active_write_allowed():
    pkg = _valid_promotion_package()
    pkg["boundary_confirmations"]["active_write_allowed"] = True
    result = validate_promotion_package_for_orchestration(pkg)
    assert result["valid"] is False
    assert any("boundary_confirmations" in e for e in result["errors"])


# --- build_promotion_steps ---


def test_build_promotion_steps_both():
    pkg = _valid_promotion_package()
    steps = build_promotion_steps(pkg)
    assert len(steps) == 2
    assert steps[0].step_id == "step_01_branches_persist"
    assert steps[0].target_api == "/branches/persist"
    assert steps[0].execution_allowed_in_p3_m4 is False
    assert steps[1].step_id == "step_02_alters_persist_batch"
    assert steps[1].target_api == "/alters/persist-batch"
    assert steps[1].execution_allowed_in_p3_m4 is False


def test_build_promotion_steps_branches_only():
    pkg = _valid_promotion_package()
    pkg["target_persist_apis"] = ["/branches/persist"]
    del pkg["alters_payload"]
    steps = build_promotion_steps(pkg)
    assert len(steps) == 1
    assert steps[0].step_id == "step_01_branches_persist"


def test_build_promotion_steps_alters_only():
    pkg = _valid_promotion_package()
    pkg["target_persist_apis"] = ["/alters/persist-batch"]
    del pkg["branches_payload"]
    steps = build_promotion_steps(pkg)
    assert len(steps) == 1
    assert steps[0].step_id == "step_02_alters_persist_batch"


def test_all_steps_execution_allowed_false():
    pkg = _valid_promotion_package()
    steps = build_promotion_steps(pkg)
    for step in steps:
        assert step.execution_allowed_in_p3_m4 is False
        assert step.requires_human_approval is True


# --- build_evidence_requirements ---


def test_build_evidence_requirements():
    pkg = _valid_promotion_package()
    reqs = build_evidence_requirements(pkg)
    names = [r.name for r in reqs]
    assert "human_final_approval_token" in names
    assert "dry_run_branches_persist" in names
    assert "dry_run_alters_persist_batch" in names
    assert "active_yaml_diff_check" in names
    assert "audit_log_verification" in names
    assert "validation_after_execution" in names
    assert "rollback_backup_path_verification" in names


# --- build_rollback_plan ---


def test_build_rollback_plan():
    pkg = _valid_promotion_package()
    plan = build_rollback_plan(pkg)
    assert plan.rollback_available is True
    assert any("P3-M4 does not create backups" in n for n in plan.notes)
    assert "alters/current/branches.yaml" in plan.required_backups
    assert "alters/current/alters/alter_A-D.yaml" in plan.required_backups


# --- build_orchestration_plan ---


def test_build_orchestration_plan(tmp_path):
    _write_promotion_package(tmp_path, "draft_001", _valid_promotion_package())
    plan = build_orchestration_plan(tmp_path, "draft_001")
    assert plan.draft_id == "draft_001"
    assert plan.status == "promotion_plan"
    assert plan.active_execution_allowed is False
    assert plan.requires_human_final_approval is True
    assert len(plan.steps) == 2
    assert len(plan.evidence_required) >= 7


def test_build_orchestration_plan_rejects_invalid(tmp_path):
    pkg = _valid_promotion_package()
    pkg["active_write_allowed"] = True
    _write_promotion_package(tmp_path, "draft_001", pkg)
    with pytest.raises(ValueError, match="Invalid promotion package"):
        build_orchestration_plan(tmp_path, "draft_001")


# --- save_orchestration_plan ---


def test_save_orchestration_plan(tmp_path):
    _write_promotion_package(tmp_path, "draft_001", _valid_promotion_package())
    plan = build_orchestration_plan(tmp_path, "draft_001")
    result = save_orchestration_plan(tmp_path, "draft_001", plan, "token-123")
    assert result["status"] == "plan_saved"
    assert (tmp_path / "draft_001" / "promotion_orchestration_plan.yaml").exists()


def test_save_orchestration_plan_rejects_blank_token(tmp_path):
    _write_promotion_package(tmp_path, "draft_001", _valid_promotion_package())
    plan = build_orchestration_plan(tmp_path, "draft_001")
    with pytest.raises(ValueError, match="approval_token"):
        save_orchestration_plan(tmp_path, "draft_001", plan, "")


def test_save_orchestration_plan_no_raw_token(tmp_path):
    _write_promotion_package(tmp_path, "draft_001", _valid_promotion_package())
    plan = build_orchestration_plan(tmp_path, "draft_001")
    save_orchestration_plan(tmp_path, "draft_001", plan, "secret-token")
    content = (tmp_path / "draft_001" / "promotion_orchestration_plan.yaml").read_text()
    assert "secret-token" not in content


# --- list_orchestration_plans ---


def test_list_orchestration_plans_empty(tmp_path):
    plans = list_orchestration_plans(tmp_path / "nonexistent")
    assert plans == []


def test_list_orchestration_plans_metadata_only(tmp_path):
    _write_promotion_package(tmp_path, "draft_001", _valid_promotion_package())
    plan = build_orchestration_plan(tmp_path, "draft_001")
    save_orchestration_plan(tmp_path, "draft_001", plan, "token")
    plans = list_orchestration_plans(tmp_path)
    assert len(plans) == 1
    assert plans[0]["draft_id"] == "draft_001"
    assert plans[0]["plan_exists"] is True
    assert "promotion_plan" not in str(plans[0])


# --- extra field rejection ---


def test_request_rejects_extra():
    with pytest.raises(Exception):
        PromotionOrchestrationRequest(save_plan=False, provider={"name": "openai"})


def test_plan_step_rejects_extra():
    with pytest.raises(Exception):
        PromotionPlanStep(
            step_id="x", target_api="/branches/persist",
            payload_ref="x", purpose="x", rollback_note="x",
            evil_field=True,
        )
