"""API tests for promotion execution gate."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from fastapi.testclient import TestClient

from alters_lab.main import app

client = TestClient(app)


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


def _patch_workspace(monkeypatch, tmp_path):
    import alters_lab.api.promotion_execution_gate as mod
    monkeypatch.setattr(mod, "get_promotion_execution_gate_workspace", lambda: tmp_path / "drafts")


# --- health ---


def test_execution_gate_health():
    r = client.get("/promotion-execution-gate/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["component"] == "promotion-execution-gate"
    assert body["mode"] == "gate_only"
    assert body["dry_run_only"] is True
    assert body["live_execution_allowed"] is False
    assert body["provider_used"] is False


# --- check endpoint ---


def test_check_missing_inputs_returns_404(monkeypatch, tmp_path):
    _patch_workspace(monkeypatch, tmp_path)
    r = client.post("/promotion-execution-gate/nonexistent/check", json={})
    assert r.status_code == 404


def test_check_path_traversal_rejected(monkeypatch, tmp_path):
    _patch_workspace(monkeypatch, tmp_path)
    r = client.post("/promotion-execution-gate/../etc/passwd/check", json={})
    assert r.status_code in (400, 404, 422)


def test_check_save_false_writes_nothing(monkeypatch, tmp_path):
    _patch_workspace(monkeypatch, tmp_path)
    _write_gate_inputs(tmp_path / "drafts", "draft_001", _valid_promotion_package(), _valid_orchestration_plan())
    r = client.post("/promotion-execution-gate/draft_001/check", json={
        "run_dry_run": True, "save_report": False, "final_approval_token": "tok",
    })
    assert r.status_code == 200
    body = r.json()
    assert body["report"]["gate_passed"] is True
    assert body["report_path"] is None
    assert not (tmp_path / "drafts" / "draft_001" / "promotion_execution_gate_report.yaml").exists()


def test_check_returns_gate_passed(monkeypatch, tmp_path):
    _patch_workspace(monkeypatch, tmp_path)
    _write_gate_inputs(tmp_path / "drafts", "draft_001", _valid_promotion_package(), _valid_orchestration_plan())
    r = client.post("/promotion-execution-gate/draft_001/check", json={
        "run_dry_run": True, "final_approval_token": "tok",
    })
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "gate_passed"
    assert body["report"]["gate_passed"] is True
    assert body["report"]["execution_packet"] is not None
    assert body["report"]["execution_packet"]["execution_allowed_now"] is False
    assert body["report"]["execution_packet"]["live_execution_allowed_in_p3_m5"] is False
    assert body["report"]["execution_packet"]["requires_p3_m6_live_execution"] is True


def test_check_fails_without_token(monkeypatch, tmp_path):
    _patch_workspace(monkeypatch, tmp_path)
    _write_gate_inputs(tmp_path / "drafts", "draft_001", _valid_promotion_package(), _valid_orchestration_plan())
    r = client.post("/promotion-execution-gate/draft_001/check", json={
        "run_dry_run": True, "save_report": False,
    })
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "gate_failed"
    assert body["report"]["gate_passed"] is False


def test_check_save_true_requires_token(monkeypatch, tmp_path):
    _patch_workspace(monkeypatch, tmp_path)
    _write_gate_inputs(tmp_path / "drafts", "draft_001", _valid_promotion_package(), _valid_orchestration_plan())
    r = client.post("/promotion-execution-gate/draft_001/check", json={
        "run_dry_run": True, "save_report": True,
    })
    assert r.status_code == 422


def test_check_save_true_writes_files(monkeypatch, tmp_path):
    _patch_workspace(monkeypatch, tmp_path)
    _write_gate_inputs(tmp_path / "drafts", "draft_001", _valid_promotion_package(), _valid_orchestration_plan())
    r = client.post("/promotion-execution-gate/draft_001/check", json={
        "run_dry_run": True, "save_report": True, "final_approval_token": "tok",
    })
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "report_saved"
    assert body["report_path"] is not None
    assert body["packet_path"] is not None
    assert (tmp_path / "drafts" / "draft_001" / "promotion_execution_gate_report.yaml").exists()
    assert (tmp_path / "drafts" / "draft_001" / "promotion_execution_packet.yaml").exists()


def test_check_no_raw_token_in_response(monkeypatch, tmp_path):
    _patch_workspace(monkeypatch, tmp_path)
    _write_gate_inputs(tmp_path / "drafts", "draft_001", _valid_promotion_package(), _valid_orchestration_plan())
    r = client.post("/promotion-execution-gate/draft_001/check", json={
        "run_dry_run": True, "save_report": True, "final_approval_token": "secret",
    })
    body_str = str(r.json())
    assert "secret" not in body_str


def test_check_no_raw_token_in_saved_file(monkeypatch, tmp_path):
    _patch_workspace(monkeypatch, tmp_path)
    _write_gate_inputs(tmp_path / "drafts", "draft_001", _valid_promotion_package(), _valid_orchestration_plan())
    client.post("/promotion-execution-gate/draft_001/check", json={
        "run_dry_run": True, "save_report": True, "final_approval_token": "secret",
    })
    report_content = (tmp_path / "drafts" / "draft_001" / "promotion_execution_gate_report.yaml").read_text()
    assert "secret" not in report_content
    packet_content = (tmp_path / "drafts" / "draft_001" / "promotion_execution_packet.yaml").read_text()
    assert "secret" not in packet_content


def test_check_no_active_yaml_written(monkeypatch, tmp_path):
    _patch_workspace(monkeypatch, tmp_path)
    _write_gate_inputs(tmp_path / "drafts", "draft_001", _valid_promotion_package(), _valid_orchestration_plan())
    client.post("/promotion-execution-gate/draft_001/check", json={
        "run_dry_run": True, "save_report": True, "final_approval_token": "tok",
    })
    assert not (tmp_path / "alters").exists()


def test_check_dry_run_results_all_dry_run_only(monkeypatch, tmp_path):
    _patch_workspace(monkeypatch, tmp_path)
    _write_gate_inputs(tmp_path / "drafts", "draft_001", _valid_promotion_package(), _valid_orchestration_plan())
    r = client.post("/promotion-execution-gate/draft_001/check", json={"run_dry_run": True, "final_approval_token": "tok"})
    body = r.json()
    for dr in body["report"]["execution_packet"]["dry_run_results"]:
        assert dr["dry_run_only"] is True


# --- list ---


def test_list_returns_empty(monkeypatch, tmp_path):
    _patch_workspace(monkeypatch, tmp_path)
    r = client.get("/promotion-execution-gate/list")
    assert r.status_code == 200
    assert r.json()["count"] == 0


def test_list_returns_metadata_only(monkeypatch, tmp_path):
    _patch_workspace(monkeypatch, tmp_path)
    _write_gate_inputs(tmp_path / "drafts", "draft_001", _valid_promotion_package(), _valid_orchestration_plan())
    r = client.get("/promotion-execution-gate/list")
    assert r.json()["count"] == 1
    assert "gate_passed" not in str(r.json())


# --- extra field rejection ---


def test_check_rejects_extra_fields():
    r = client.post("/promotion-execution-gate/draft_001/check", json={
        "run_dry_run": False, "provider": {"name": "openai"},
    })
    assert r.status_code == 422


def test_check_rejects_calibration():
    r = client.post("/promotion-execution-gate/draft_001/check", json={
        "run_dry_run": False, "calibration": {"score": 0.9},
    })
    assert r.status_code == 422


# --- no forbidden routers ---


def test_no_forbidden_routers():
    from alters_lab.main import app as _app
    routes = [route.path for route in _app.routes]
    for forbidden in ["dialogue", "calibration", "archive"]:
        for route in routes:
            if forbidden in route.lower() and route != "/health" and not route.startswith("/alter-dialogue") and not route.startswith("/calibration-loop"):
                pytest.fail(f"Unexpected route: {route}")


# --- no provider imports ---


def test_no_provider_imports():
    import ast
    from pathlib import Path
    api_dir = Path(__file__).resolve().parent.parent / "src" / "alters_lab" / "api"
    for py_file in api_dir.glob("promotion_execution_gate.py"):
        tree = ast.parse(py_file.read_text())
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                mod = getattr(node, "module", None) or ""
                names = [a.name for a in getattr(node, "names", [])]
                for forbidden in ["openai", "anthropic", "openrouter", "litellm", "langchain", "crewai"]:
                    if forbidden in mod or any(forbidden in n for n in names):
                        pytest.fail(f"Provider import found: {forbidden}")


# --- no persist API calls ---


def test_no_persist_api_calls():
    import ast
    from pathlib import Path
    service_file = Path(__file__).resolve().parent.parent / "src" / "alters_lab" / "services" / "promotion_execution_gate.py"
    tree = ast.parse(service_file.read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Attribute):
                if func.attr in ("write_branches_with_audit", "write_alter_with_audit", "write_alter_batch_with_audit"):
                    pytest.fail(f"Persist API call found: {func.attr}")


# --- route inventory ---


def test_route_inventory():
    from alters_lab.main import app as _app
    routes = sorted(route.path for route in _app.routes)
    assert "/promotion-execution-gate/health" in routes
    assert "/promotion-execution-gate/{draft_id}/check" in routes
    assert "/promotion-execution-gate/list" in routes
    assert "/promotion-orchestration/health" in routes
    assert "/promotion-orchestration/{draft_id}/plan" in routes
    assert "/draft-review/{draft_id}/review" in routes
    assert "/generation-drafts/preview" in routes
    assert "/branches/persist" in routes
    assert "/alters/persist-batch" in routes
