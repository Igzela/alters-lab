"""Service tests for promotion execution gate."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from alters_lab.schemas.promotion_execution_gate import (
    DryRunCheckResult,
    ExecutionPacket,
    ExecutionPrerequisiteCheck,
    PromotionExecutionGateBoundaryConfirmations,
    PromotionExecutionGateRequest,
    PromotionExecutionGateReport,
)
from alters_lab.services.promotion_execution_gate import (
    build_execution_packet,
    build_gate_report,
    build_prerequisite_checks,
    compare_package_and_plan,
    list_execution_gate_reports,
    load_gate_inputs,
    promotion_execution_gate_boundary_confirmations,
    run_dry_run_compatibility_checks,
    save_gate_report,
    validate_draft_id,
    validate_orchestration_plan_for_execution_gate,
    validate_promotion_package_for_execution_gate,
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
                {"id": f"branch_{c}", "label": f"Branch {c}", "incompatible_with": [f"branch_{x}" for x in "ABCD" if x != c]}
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


def _valid_orchestration_plan() -> dict:
    return {
        "draft_id": "draft_test_001",
        "schema_version": 1,
        "status": "promotion_plan",
        "source_promotion_package_ref": "draft_test_001/promotion_package.yaml",
        "active_execution_allowed": False,
        "requires_human_final_approval": True,
        "steps": [
            {
                "step_id": "step_01_branches_persist",
                "target_api": "/branches/persist",
                "payload_ref": "promotion_package.branches_payload",
                "purpose": "Persist reviewed branches",
                "execution_allowed_in_p3_m4": False,
                "requires_human_approval": True,
                "rollback_note": "backup available",
            },
            {
                "step_id": "step_02_alters_persist_batch",
                "target_api": "/alters/persist-batch",
                "payload_ref": "promotion_package.alters_payload",
                "purpose": "Persist reviewed alters",
                "execution_allowed_in_p3_m4": False,
                "requires_human_approval": True,
                "rollback_note": "backup available",
            },
        ],
        "evidence_required": [
            {"name": "human_final_approval", "required": True, "description": "Human approval"},
        ],
        "rollback_plan": {"rollback_available": True, "notes": ["backup"], "required_backups": ["branches.yaml"]},
        "boundary_confirmations": {"plan_only": True, "controlled_persist_api_called": False},
        "created_at": "2026-05-19T00:00:00Z",
    }


def _write_gate_inputs(workspace: Path, draft_id: str, pkg: dict, plan: dict):
    d = workspace / draft_id
    d.mkdir(parents=True, exist_ok=True)
    (d / "promotion_package.yaml").write_text(yaml.dump(pkg), encoding="utf-8")
    (d / "promotion_orchestration_plan.yaml").write_text(yaml.dump(plan), encoding="utf-8")


# --- boundary confirmations ---


def test_boundary_confirmations_all_false():
    bc = promotion_execution_gate_boundary_confirmations()
    assert bc["gate_only"] is True
    assert bc["dry_run_only"] is True
    assert bc["active_yaml_modified"] is False
    assert bc["live_persist_called"] is False
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


# --- load_gate_inputs ---


def test_load_gate_inputs(tmp_path):
    _write_gate_inputs(tmp_path, "draft_001", _valid_promotion_package(), _valid_orchestration_plan())
    inputs = load_gate_inputs(tmp_path, "draft_001")
    assert inputs["promotion_package"]["draft_id"] == "draft_test_001"
    assert inputs["orchestration_plan"]["status"] == "promotion_plan"


def test_load_gate_inputs_rejects_missing_package(tmp_path):
    plan = _valid_orchestration_plan()
    d = tmp_path / "draft_001"
    d.mkdir(parents=True)
    (d / "promotion_orchestration_plan.yaml").write_text(yaml.dump(plan))
    with pytest.raises(FileNotFoundError):
        load_gate_inputs(tmp_path, "draft_001")


def test_load_gate_inputs_rejects_missing_plan(tmp_path):
    pkg = _valid_promotion_package()
    d = tmp_path / "draft_001"
    d.mkdir(parents=True)
    (d / "promotion_package.yaml").write_text(yaml.dump(pkg))
    with pytest.raises(FileNotFoundError):
        load_gate_inputs(tmp_path, "draft_001")


def test_load_gate_inputs_rejects_path_traversal(tmp_path):
    with pytest.raises(ValueError, match="path traversal"):
        load_gate_inputs(tmp_path, "../etc/passwd")


# --- validate_orchestration_plan_for_execution_gate ---


def test_validate_plan_passes():
    result = validate_orchestration_plan_for_execution_gate(_valid_orchestration_plan())
    assert result["valid"] is True
    assert result["errors"] == []


def test_validate_plan_rejects_wrong_status():
    plan = _valid_orchestration_plan()
    plan["status"] = "draft"
    result = validate_orchestration_plan_for_execution_gate(plan)
    assert result["valid"] is False
    assert any("status" in e for e in result["errors"])


def test_validate_plan_rejects_active_execution_allowed():
    plan = _valid_orchestration_plan()
    plan["active_execution_allowed"] = True
    result = validate_orchestration_plan_for_execution_gate(plan)
    assert result["valid"] is False
    assert any("active_execution_allowed" in e for e in result["errors"])


def test_validate_plan_rejects_empty_steps():
    plan = _valid_orchestration_plan()
    plan["steps"] = []
    result = validate_orchestration_plan_for_execution_gate(plan)
    assert result["valid"] is False
    assert any("empty" in e for e in result["errors"])


def test_validate_plan_rejects_execution_allowed_true():
    plan = _valid_orchestration_plan()
    plan["steps"][0]["execution_allowed_in_p3_m4"] = True
    result = validate_orchestration_plan_for_execution_gate(plan)
    assert result["valid"] is False
    assert any("execution_allowed_in_p3_m4" in e for e in result["errors"])


def test_validate_plan_rejects_invalid_target_api():
    plan = _valid_orchestration_plan()
    plan["steps"][0]["target_api"] = "/evil/api"
    result = validate_orchestration_plan_for_execution_gate(plan)
    assert result["valid"] is False
    assert any("not in allowed" in e for e in result["errors"])


def test_validate_plan_rejects_empty_evidence():
    plan = _valid_orchestration_plan()
    plan["evidence_required"] = []
    result = validate_orchestration_plan_for_execution_gate(plan)
    assert result["valid"] is False
    assert any("evidence_required" in e for e in result["errors"])


# --- validate_promotion_package_for_execution_gate ---


def test_validate_package_passes():
    result = validate_promotion_package_for_execution_gate(_valid_promotion_package())
    assert result["valid"] is True


def test_validate_package_rejects_active_write_allowed():
    pkg = _valid_promotion_package()
    pkg["active_write_allowed"] = True
    result = validate_promotion_package_for_execution_gate(pkg)
    assert result["valid"] is False
    assert any("active_write_allowed" in e for e in result["errors"])


def test_validate_package_rejects_wrong_status():
    pkg = _valid_promotion_package()
    pkg["status"] = "draft"
    result = validate_promotion_package_for_execution_gate(pkg)
    assert result["valid"] is False
    assert any("status" in e for e in result["errors"])


def test_validate_package_rejects_invalid_target_api():
    pkg = _valid_promotion_package()
    pkg["target_persist_apis"] = ["/evil"]
    result = validate_promotion_package_for_execution_gate(pkg)
    assert result["valid"] is False


def test_validate_package_rejects_branches_not_exactly_ad():
    pkg = _valid_promotion_package()
    pkg["branches_payload"]["branches"] = [{"id": "branch_A", "label": "A", "incompatible_with": []}]
    result = validate_promotion_package_for_execution_gate(pkg)
    assert result["valid"] is False
    assert any("branches count" in e for e in result["errors"])


def test_validate_package_rejects_alters_bad_source_refs():
    pkg = _valid_promotion_package()
    pkg["alters_payload"]["alters"][0]["source_refs"]["snapshot_ref"] = "wrong"
    result = validate_promotion_package_for_execution_gate(pkg)
    assert result["valid"] is False
    assert any("source_refs" in e for e in result["errors"])


def test_validate_package_rejects_alter_human_confirmed_false():
    pkg = _valid_promotion_package()
    pkg["alters_payload"]["alters"][0]["quality_status"]["human_confirmed"] = False
    result = validate_promotion_package_for_execution_gate(pkg)
    assert result["valid"] is False
    assert any("human_confirmed" in e for e in result["errors"])


# --- compare_package_and_plan ---


def test_compare_passes():
    pkg = _valid_promotion_package()
    plan = _valid_orchestration_plan()
    result = compare_package_and_plan(pkg, plan)
    assert result["valid"] is True


def test_compare_rejects_apis_mismatch():
    pkg = _valid_promotion_package()
    pkg["target_persist_apis"] = ["/branches/persist"]
    plan = _valid_orchestration_plan()
    result = compare_package_and_plan(pkg, plan)
    assert result["valid"] is False
    assert any("mismatch" in e for e in result["errors"])


def test_compare_rejects_missing_branches_step():
    pkg = _valid_promotion_package()
    plan = _valid_orchestration_plan()
    plan["steps"] = [plan["steps"][1]]  # only alters step
    result = compare_package_and_plan(pkg, plan)
    assert result["valid"] is False
    assert any("branches_payload" in e for e in result["errors"])


def test_compare_rejects_wrong_step_order():
    pkg = _valid_promotion_package()
    plan = _valid_orchestration_plan()
    plan["steps"] = [plan["steps"][1], plan["steps"][0]]  # swapped
    result = compare_package_and_plan(pkg, plan)
    assert result["valid"] is False
    assert any("ordering" in e for e in result["errors"])


def test_compare_rejects_draft_id_mismatch():
    pkg = _valid_promotion_package()
    pkg["draft_id"] = "draft_other"
    plan = _valid_orchestration_plan()
    result = compare_package_and_plan(pkg, plan)
    assert result["valid"] is False
    assert any("draft_id mismatch" in e for e in result["errors"])


# --- build_prerequisite_checks ---


def test_build_prerequisites():
    pkg = _valid_promotion_package()
    plan = _valid_orchestration_plan()
    checks = build_prerequisite_checks(pkg, plan, "token")
    names = [c.name for c in checks]
    assert "promotion_package_valid" in names
    assert "orchestration_plan_valid" in names
    assert "package_plan_consistency" in names
    assert "final_approval_token_present" in names
    assert all(c.passed for c in checks)


def test_build_prerequisites_fails_without_token():
    pkg = _valid_promotion_package()
    plan = _valid_orchestration_plan()
    checks = build_prerequisite_checks(pkg, plan, None)
    token_check = next(c for c in checks if c.name == "final_approval_token_present")
    assert token_check.passed is False


# --- run_dry_run_compatibility_checks ---


def test_dry_run_checks_both():
    pkg = _valid_promotion_package()
    results = run_dry_run_compatibility_checks(pkg)
    assert len(results) == 2
    assert all(dr.dry_run_only is True for dr in results)
    assert all(dr.passed for dr in results)


def test_dry_run_checks_branches_only():
    pkg = _valid_promotion_package()
    del pkg["alters_payload"]
    results = run_dry_run_compatibility_checks(pkg)
    assert len(results) == 1
    assert results[0].target_api == "/branches/persist"


def test_dry_run_fails_bad_branches():
    pkg = _valid_promotion_package()
    pkg["branches_payload"]["branches"] = [{"id": "branch_A", "label": "A", "incompatible_with": []}]
    results = run_dry_run_compatibility_checks(pkg)
    assert any(not dr.passed for dr in results)


# --- build_execution_packet ---


def test_build_execution_packet():
    pkg = _valid_promotion_package()
    plan = _valid_orchestration_plan()
    prereqs = build_prerequisite_checks(pkg, plan, "token")
    dry_runs = run_dry_run_compatibility_checks(pkg)
    packet = build_execution_packet("draft_001", pkg, plan, dry_runs, prereqs, "token")
    assert packet.execution_allowed_now is False
    assert packet.live_execution_allowed_in_p3_m5 is False
    assert packet.requires_p3_m6_live_execution is True
    assert packet.final_approval_token_hash is not None


def test_build_execution_packet_no_token():
    pkg = _valid_promotion_package()
    plan = _valid_orchestration_plan()
    prereqs = build_prerequisite_checks(pkg, plan, None)
    dry_runs = run_dry_run_compatibility_checks(pkg)
    packet = build_execution_packet("draft_001", pkg, plan, dry_runs, prereqs, None)
    assert packet.final_approval_token_hash is None


# --- build_gate_report ---


def test_build_gate_report_passes():
    pkg = _valid_promotion_package()
    plan = _valid_orchestration_plan()
    report = build_gate_report("draft_001", pkg, plan, True, "token")
    assert report.gate_passed is True
    assert report.status == "gate_passed"
    assert report.execution_packet is not None
    assert report.execution_packet.execution_allowed_now is False


def test_build_gate_report_fails_without_token():
    pkg = _valid_promotion_package()
    plan = _valid_orchestration_plan()
    report = build_gate_report("draft_001", pkg, plan, True, None)
    assert report.gate_passed is False
    assert report.status == "gate_failed"
    assert report.execution_packet is None
    assert "final_approval_token_present" in report.blocking_failures


def test_build_gate_report_no_dry_run():
    pkg = _valid_promotion_package()
    plan = _valid_orchestration_plan()
    report = build_gate_report("draft_001", pkg, plan, False, "token")
    assert report.gate_passed is True


# --- save_gate_report ---


def test_save_gate_report(tmp_path):
    pkg = _valid_promotion_package()
    plan = _valid_orchestration_plan()
    report = build_gate_report("draft_001", pkg, plan, True, "token")
    result = save_gate_report(tmp_path, "draft_001", report, "token")
    assert result["status"] == "report_saved"
    assert (tmp_path / "draft_001" / "promotion_execution_gate_report.yaml").exists()
    assert (tmp_path / "draft_001" / "promotion_execution_packet.yaml").exists()


def test_save_gate_report_rejects_blank_token(tmp_path):
    pkg = _valid_promotion_package()
    plan = _valid_orchestration_plan()
    report = build_gate_report("draft_001", pkg, plan, True, "token")
    with pytest.raises(ValueError, match="final_approval_token"):
        save_gate_report(tmp_path, "draft_001", report, "")


def test_save_gate_report_no_raw_token(tmp_path):
    pkg = _valid_promotion_package()
    plan = _valid_orchestration_plan()
    report = build_gate_report("draft_001", pkg, plan, True, "token")
    save_gate_report(tmp_path, "draft_001", report, "secret-token")
    content = (tmp_path / "draft_001" / "promotion_execution_gate_report.yaml").read_text()
    assert "secret-token" not in content


# --- list_execution_gate_reports ---


def test_list_reports_empty(tmp_path):
    reports = list_execution_gate_reports(tmp_path / "nonexistent")
    assert reports == []


def test_list_reports_metadata_only(tmp_path):
    pkg = _valid_promotion_package()
    plan = _valid_orchestration_plan()
    _write_gate_inputs(tmp_path, "draft_001", pkg, plan)
    report = build_gate_report("draft_001", pkg, plan, True, "token")
    save_gate_report(tmp_path, "draft_001", report, "token")
    reports = list_execution_gate_reports(tmp_path)
    assert len(reports) == 1
    assert reports[0]["draft_id"] == "draft_001"
    assert reports[0]["report_exists"] is True
    assert "gate_passed" not in str(reports[0])


# --- extra field rejection ---


def test_request_rejects_extra():
    with pytest.raises(Exception):
        PromotionExecutionGateRequest(run_dry_run=False, provider={"name": "openai"})


def test_report_rejects_extra():
    with pytest.raises(Exception):
        PromotionExecutionGateReport(
            draft_id="x", status="gate_passed", gate_passed=True,
            blocking_failures=[], warnings=[],
            boundary_confirmations=PromotionExecutionGateBoundaryConfirmations(),
            created_at="x", evil_field=True,
        )
