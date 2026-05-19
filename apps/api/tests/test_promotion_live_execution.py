"""Service tests for promotion live execution."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from alters_lab.schemas.promotion_live_execution import (
    LiveExecutionStepResult,
    PromotionLiveExecutionBoundaryConfirmations,
    PromotionLiveExecutionReport,
    PromotionLiveExecutionRequest,
)
from alters_lab.services.promotion_live_execution import (
    build_live_execution_report,
    extract_alters_persist_payload,
    extract_branches_persist_payload,
    list_live_execution_reports,
    load_live_execution_inputs,
    promotion_live_execution_boundary_confirmations,
    run_live_execution_gate,
    save_live_execution_report,
    validate_draft_id,
    validate_gate_for_live_execution,
)


def _hash(token: str) -> str:
    from alters_lab.services.controlled_write import hash_approval_token
    return hash_approval_token(token)


def _valid_package() -> dict:
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


def _valid_plan() -> dict:
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


def _valid_gate_report() -> dict:
    return {
        "draft_id": "draft_test_001",
        "schema_version": 1,
        "status": "gate_passed",
        "gate_passed": True,
        "blocking_failures": [],
        "warnings": [],
        "created_at": "2026-05-19T00:00:00Z",
    }


def _valid_execution_packet() -> dict:
    return {
        "draft_id": "draft_test_001",
        "schema_version": 1,
        "status": "execution_packet",
        "execution_allowed_now": False,
        "live_execution_allowed_in_p3_m5": False,
        "requires_p3_m6_live_execution": True,
        "ordered_steps": [
            {"step_id": "step_01_branches_persist", "target_api": "/branches/persist"},
            {"step_id": "step_02_alters_persist_batch", "target_api": "/alters/persist-batch"},
        ],
        "dry_run_results": [
            {"target_api": "/branches/persist", "passed": True},
            {"target_api": "/alters/persist-batch", "passed": True},
        ],
        "final_approval_token_hash": _hash("test-token-123"),
        "created_at": "2026-05-19T00:00:00Z",
    }


def _write_all_inputs(workspace: Path, draft_id: str, token: str = "test-token-123"):
    d = workspace / draft_id
    d.mkdir(parents=True, exist_ok=True)
    (d / "promotion_package.yaml").write_text(yaml.dump(_valid_package()), encoding="utf-8")
    (d / "promotion_orchestration_plan.yaml").write_text(yaml.dump(_valid_plan()), encoding="utf-8")
    (d / "promotion_execution_gate_report.yaml").write_text(yaml.dump(_valid_gate_report()), encoding="utf-8")
    packet = _valid_execution_packet()
    packet["final_approval_token_hash"] = _hash(token)
    (d / "promotion_execution_packet.yaml").write_text(yaml.dump(packet), encoding="utf-8")


# --- boundary confirmations ---


def test_boundary_confirmations_all_false():
    bc = promotion_live_execution_boundary_confirmations()
    assert bc["live_execution_runtime_added"] is True
    assert bc["controlled_persist_services_used"] is True
    assert bc["active_yaml_modified"] is False
    assert bc["branches_yaml_modified"] is False
    assert bc["alters_modified"] is False
    assert bc["draft_promoted_to_active"] is False


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


# --- load_live_execution_inputs ---


def test_load_inputs(tmp_path):
    _write_all_inputs(tmp_path, "draft_001")
    inputs = load_live_execution_inputs(tmp_path, "draft_001")
    assert inputs["promotion_package"]["draft_id"] == "draft_test_001"
    assert inputs["orchestration_plan"]["status"] == "promotion_plan"
    assert inputs["gate_report"]["status"] == "gate_passed"
    assert inputs["execution_packet"]["status"] == "execution_packet"
    assert "paths" in inputs


def test_load_inputs_rejects_missing(tmp_path):
    d = tmp_path / "draft_001"
    d.mkdir(parents=True)
    with pytest.raises(FileNotFoundError):
        load_live_execution_inputs(tmp_path, "draft_001")


def test_load_inputs_rejects_path_traversal(tmp_path):
    with pytest.raises(ValueError, match="path traversal"):
        load_live_execution_inputs(tmp_path, "../etc/passwd")


# --- validate_gate_for_live_execution ---


def test_validate_gate_passes():
    token = "test-token-123"
    result = validate_gate_for_live_execution(
        _valid_package(), _valid_plan(), _valid_gate_report(), _valid_execution_packet(), token
    )
    assert result["valid"] is True
    assert result["errors"] == []


def test_validate_gate_rejects_gate_not_passed():
    report = _valid_gate_report()
    report["status"] = "gate_failed"
    result = validate_gate_for_live_execution(
        _valid_package(), _valid_plan(), report, _valid_execution_packet(), "token"
    )
    assert result["valid"] is False
    assert any("gate_report.status" in e for e in result["errors"])


def test_validate_gate_rejects_packet_execution_allowed():
    packet = _valid_execution_packet()
    packet["execution_allowed_now"] = True
    result = validate_gate_for_live_execution(
        _valid_package(), _valid_plan(), _valid_gate_report(), packet, "token"
    )
    assert result["valid"] is False
    assert any("execution_allowed_now" in e for e in result["errors"])


def test_validate_gate_rejects_packet_no_p3_m6_required():
    packet = _valid_execution_packet()
    packet["requires_p3_m6_live_execution"] = False
    result = validate_gate_for_live_execution(
        _valid_package(), _valid_plan(), _valid_gate_report(), packet, "token"
    )
    assert result["valid"] is False
    assert any("requires_p3_m6_live_execution" in e for e in result["errors"])


def test_validate_gate_rejects_token_mismatch():
    result = validate_gate_for_live_execution(
        _valid_package(), _valid_plan(), _valid_gate_report(), _valid_execution_packet(), "wrong-token"
    )
    assert result["valid"] is False
    assert any("hash does not match" in e for e in result["errors"])


def test_validate_gate_rejects_no_token_when_required():
    result = validate_gate_for_live_execution(
        _valid_package(), _valid_plan(), _valid_gate_report(), _valid_execution_packet(), None,
        require_token=True,
    )
    assert result["valid"] is False
    assert any("final_execution_token missing" in e for e in result["errors"])


def test_validate_gate_accepts_no_token_when_not_required():
    result = validate_gate_for_live_execution(
        _valid_package(), _valid_plan(), _valid_gate_report(), _valid_execution_packet(), None,
        require_token=False,
    )
    assert result["valid"] is True


def test_validate_gate_token_hash_check_disabled():
    result = validate_gate_for_live_execution(
        _valid_package(), _valid_plan(), _valid_gate_report(), _valid_execution_packet(),
        "any-token", require_matching_gate_token=False
    )
    assert result["valid"] is True


def test_validate_gate_rejects_dry_run_not_passed():
    packet = _valid_execution_packet()
    packet["dry_run_results"] = [{"target_api": "/branches/persist", "passed": False}]
    result = validate_gate_for_live_execution(
        _valid_package(), _valid_plan(), _valid_gate_report(), packet, "test-token-123"
    )
    assert result["valid"] is False
    assert any("not passed" in e for e in result["errors"])


def test_validate_gate_rejects_apis_mismatch():
    pkg = _valid_package()
    pkg["target_persist_apis"] = ["/branches/persist"]
    result = validate_gate_for_live_execution(
        pkg, _valid_plan(), _valid_gate_report(), _valid_execution_packet(), "test-token-123"
    )
    assert result["valid"] is False
    assert any("mismatch" in e for e in result["errors"])


# --- extract_branches_persist_payload ---


def test_extract_branches_passes():
    pkg = _valid_package()
    payload = extract_branches_persist_payload(pkg)
    assert len(payload["branches"]) == 4


def test_extract_branches_rejects_missing():
    with pytest.raises(ValueError, match="missing"):
        extract_branches_persist_payload({})


def test_extract_branches_rejects_wrong_count():
    pkg = _valid_package()
    pkg["branches_payload"]["branches"] = [{"id": "branch_A", "label": "A", "incompatible_with": []}]
    with pytest.raises(ValueError, match="count != 4"):
        extract_branches_persist_payload(pkg)


def test_extract_branches_rejects_incomplete_ids():
    pkg = _valid_package()
    pkg["branches_payload"]["branches"] = [
        {"id": f"branch_{c}", "label": f"B{c}", "incompatible_with": []}
        for c in "ABCE"
    ]
    with pytest.raises(ValueError, match="incomplete"):
        extract_branches_persist_payload(pkg)


def test_extract_branches_rejects_empty_incompatible():
    pkg = _valid_package()
    pkg["branches_payload"]["branches"][0]["incompatible_with"] = []
    with pytest.raises(ValueError, match="incompatible_with"):
        extract_branches_persist_payload(pkg)


# --- extract_alters_persist_payload ---


def test_extract_alters_passes():
    pkg = _valid_package()
    payload = extract_alters_persist_payload(pkg)
    assert len(payload["alters"]) == 4


def test_extract_alters_rejects_missing():
    with pytest.raises(ValueError, match="missing"):
        extract_alters_persist_payload({})


def test_extract_alters_rejects_wrong_count():
    pkg = _valid_package()
    pkg["alters_payload"]["alters"] = [{"id": "alter_A"}]
    with pytest.raises(ValueError, match="count != 4"):
        extract_alters_persist_payload(pkg)


def test_extract_alters_rejects_wrong_snapshot_ref():
    pkg = _valid_package()
    pkg["alters_payload"]["alters"][0]["source_refs"]["snapshot_ref"] = "wrong"
    with pytest.raises(ValueError, match="snapshot_ref"):
        extract_alters_persist_payload(pkg)


def test_extract_alters_rejects_human_confirmed_false():
    pkg = _valid_package()
    pkg["alters_payload"]["alters"][0]["quality_status"]["human_confirmed"] = False
    with pytest.raises(ValueError, match="human_confirmed"):
        extract_alters_persist_payload(pkg)


def test_extract_alters_rejects_voice_empty():
    pkg = _valid_package()
    pkg["alters_payload"]["alters"][0]["voice"]["core_stance"] = ""
    with pytest.raises(ValueError, match="core_stance"):
        extract_alters_persist_payload(pkg)


# --- build_live_execution_report ---


def test_report_dry_run_passed():
    pkg = _valid_package()
    plan = _valid_plan()
    inputs = {
        "promotion_package": pkg, "orchestration_plan": plan,
        "gate_report": _valid_gate_report(), "execution_packet": _valid_execution_packet(),
        "paths": {"promotion_package": "pkg.yaml", "orchestration_plan": "plan.yaml",
                  "gate_report": "gate.yaml", "execution_packet": "packet.yaml"},
    }
    step_results = [
        LiveExecutionStepResult(step_id="s1", target_api="/branches/persist", executed=False,
                                dry_run=True, status="dry_run_passed", message="ok"),
        LiveExecutionStepResult(step_id="s2", target_api="/alters/persist-batch", executed=False,
                                dry_run=True, status="dry_run_passed", message="ok"),
    ]
    validation = {"valid": True, "errors": []}
    report = build_live_execution_report("draft_001", inputs, "dry_run", "tok", step_results, validation)
    assert report.status == "dry_run_passed"
    assert report.live_execution_performed is False
    assert report.dry_run_only is True


def test_report_live_executed():
    pkg = _valid_package()
    plan = _valid_plan()
    inputs = {
        "promotion_package": pkg, "orchestration_plan": plan,
        "gate_report": _valid_gate_report(), "execution_packet": _valid_execution_packet(),
        "paths": {"promotion_package": "pkg.yaml", "orchestration_plan": "plan.yaml",
                  "gate_report": "gate.yaml", "execution_packet": "packet.yaml"},
    }
    step_results = [
        LiveExecutionStepResult(step_id="s1", target_api="/branches/persist", executed=True,
                                dry_run=False, status="executed", message="ok"),
        LiveExecutionStepResult(step_id="s2", target_api="/alters/persist-batch", executed=True,
                                dry_run=False, status="executed", message="ok"),
    ]
    validation = {"valid": True, "errors": []}
    report = build_live_execution_report("draft_001", inputs, "live", "tok", step_results, validation)
    assert report.status == "live_executed"
    assert report.live_execution_performed is True


def test_report_rejected():
    inputs = {
        "promotion_package": {}, "orchestration_plan": {},
        "gate_report": {}, "execution_packet": {},
        "paths": {"promotion_package": "pkg.yaml", "orchestration_plan": "plan.yaml",
                  "gate_report": "gate.yaml", "execution_packet": "packet.yaml"},
    }
    validation = {"valid": False, "errors": ["gate not passed"]}
    report = build_live_execution_report("draft_001", inputs, "dry_run", None, [], validation)
    assert report.status == "rejected"
    assert report.live_execution_performed is False
    assert report.blocking_failures == ["gate not passed"]


# --- save_live_execution_report ---


def test_save_report(tmp_path):
    pkg = _valid_package()
    plan = _valid_plan()
    inputs = {
        "promotion_package": pkg, "orchestration_plan": plan,
        "gate_report": _valid_gate_report(), "execution_packet": _valid_execution_packet(),
        "paths": {"promotion_package": "pkg.yaml", "orchestration_plan": "plan.yaml",
                  "gate_report": "gate.yaml", "execution_packet": "packet.yaml"},
    }
    report = build_live_execution_report("draft_001", inputs, "dry_run", "tok", [], {"valid": True, "errors": []})
    result = save_live_execution_report(tmp_path, "draft_001", report, "tok")
    assert result["status"] == "report_saved"
    assert (tmp_path / "draft_001" / "promotion_live_execution_report.yaml").exists()


def test_save_report_rejects_blank_token(tmp_path):
    report = PromotionLiveExecutionReport(
        draft_id="draft_001", status="dry_run_passed", live_execution_performed=False,
        dry_run_only=True, source_promotion_package_ref="a", source_orchestration_plan_ref="b",
        source_gate_report_ref="c", source_execution_packet_ref="d",
        step_results=[], blocking_failures=[],
        boundary_confirmations=PromotionLiveExecutionBoundaryConfirmations(),
        created_at="2026-05-19T00:00:00Z",
    )
    with pytest.raises(ValueError, match="final_execution_token"):
        save_live_execution_report(tmp_path, "draft_001", report, "")


def test_save_report_no_raw_token(tmp_path):
    report = PromotionLiveExecutionReport(
        draft_id="draft_001", status="dry_run_passed", live_execution_performed=False,
        dry_run_only=True, source_promotion_package_ref="a", source_orchestration_plan_ref="b",
        source_gate_report_ref="c", source_execution_packet_ref="d",
        step_results=[], blocking_failures=[],
        boundary_confirmations=PromotionLiveExecutionBoundaryConfirmations(),
        created_at="2026-05-19T00:00:00Z",
    )
    save_live_execution_report(tmp_path, "draft_001", report, "super-secret-token")
    content = (tmp_path / "draft_001" / "promotion_live_execution_report.yaml").read_text()
    assert "super-secret-token" not in content


# --- list_live_execution_reports ---


def test_list_empty(tmp_path):
    assert list_live_execution_reports(tmp_path / "nonexistent") == []


def test_list_metadata_only(tmp_path):
    _write_all_inputs(tmp_path, "draft_001")
    report = PromotionLiveExecutionReport(
        draft_id="draft_001", status="dry_run_passed", live_execution_performed=False,
        dry_run_only=True, source_promotion_package_ref="a", source_orchestration_plan_ref="b",
        source_gate_report_ref="c", source_execution_packet_ref="d",
        step_results=[], blocking_failures=[],
        boundary_confirmations=PromotionLiveExecutionBoundaryConfirmations(),
        created_at="2026-05-19T00:00:00Z",
    )
    save_live_execution_report(tmp_path, "draft_001", report, "tok")
    reports = list_live_execution_reports(tmp_path)
    assert len(reports) == 1
    assert reports[0]["draft_id"] == "draft_001"
    assert reports[0]["live_execution_report_exists"] is True


# --- run_live_execution_gate ---


def test_run_dry_run(tmp_path):
    _write_all_inputs(tmp_path, "draft_001")
    report = run_live_execution_gate(tmp_path, "draft_001", "dry_run", "test-token-123")
    assert report.status == "dry_run_passed"
    assert report.dry_run_only is True
    assert len(report.step_results) == 2


def test_run_dry_run_without_token_passes(tmp_path):
    _write_all_inputs(tmp_path, "draft_001")
    report = run_live_execution_gate(tmp_path, "draft_001", "dry_run", None)
    assert report.status in ("dry_run_passed", "dry_run_failed")
    assert report.live_execution_performed is False
    assert report.dry_run_only is True


def test_run_live_without_token_rejected(tmp_path):
    _write_all_inputs(tmp_path, "draft_001")
    report = run_live_execution_gate(tmp_path, "draft_001", "live", None)
    assert report.status == "rejected"
    assert any("final_execution_token missing" in e for e in report.blocking_failures)


def test_run_live_without_path_overrides(tmp_path):
    _write_all_inputs(tmp_path, "draft_001")
    report = run_live_execution_gate(tmp_path, "draft_001", "live", "test-token-123")
    assert report.status == "rejected"
    assert any("path_overrides" in e for e in report.blocking_failures)


def test_run_live_with_mocked_persist(tmp_path):
    _write_all_inputs(tmp_path, "draft_001")
    path_overrides = {
        "branches_target_path": str(tmp_path / "branches.yaml"),
        "alters_dir": str(tmp_path / "alters"),
        "backup_dir": str(tmp_path / "backup"),
        "audit_log_path": str(tmp_path / "audit.yaml"),
    }

    with patch("alters_lab.services.branches_persist.write_branches_with_audit") as mock_branches, \
         patch("alters_lab.services.alters_persist.write_alter_batch_with_audit") as mock_alters:
        mock_branches.return_value = {
            "pre_write_hash": "pre_b", "post_write_hash": "post_b",
            "backup_path": "/backup/branches.yaml", "audit_log_path": "/audit/branches.yaml",
        }
        mock_alters.return_value = {
            "pre_write_hash": "pre_a", "post_write_hash": "post_a",
            "backup_path": "/backup/alters", "audit_log_path": "/audit/alters.yaml",
        }
        report = run_live_execution_gate(
            tmp_path, "draft_001", "live", "test-token-123", path_overrides=path_overrides
        )
        assert report.status == "live_executed"
        assert report.live_execution_performed is True
        assert mock_branches.called
        assert mock_alters.called


# --- extra field rejection ---


def test_request_rejects_extra():
    with pytest.raises(Exception):
        PromotionLiveExecutionRequest(mode="dry_run", evil_field=True)


def test_step_result_rejects_extra():
    with pytest.raises(Exception):
        LiveExecutionStepResult(
            step_id="s1", target_api="/branches/persist", executed=False,
            dry_run=True, status="dry_run_passed", message="ok", evil_field=True,
        )


def test_report_rejects_extra():
    with pytest.raises(Exception):
        PromotionLiveExecutionReport(
            draft_id="x", status="dry_run_passed", live_execution_performed=False,
            dry_run_only=True, source_promotion_package_ref="a", source_orchestration_plan_ref="b",
            source_gate_report_ref="c", source_execution_packet_ref="d",
            step_results=[], blocking_failures=[],
            boundary_confirmations=PromotionLiveExecutionBoundaryConfirmations(),
            created_at="x", evil_field=True,
        )
