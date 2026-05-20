"""API tests for promotion live execution."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from fastapi.testclient import TestClient

from alters_lab.main import app

client = TestClient(app)


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
            "branch_discovery": {"status": "completed", "source_snapshot_ref": "alters/current/snapshot.yaml", "confirmed_by": "human_owner"},
            "branches": [
                {"id": f"branch_{c}", "label": f"Branch {c}", "core_choice": f"Choice {c}", "structural_commitment": f"SC {c}", "key_tension_resolved": f"KR {c}", "incompatible_with": [f"branch_{x}" for x in "ABCD" if x != c]}
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


def _valid_execution_packet(token: str = "test-token-123") -> dict:
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
        "final_approval_token_hash": _hash(token),
        "created_at": "2026-05-19T00:00:00Z",
    }


def _write_all_inputs(workspace: Path, draft_id: str, token: str = "test-token-123"):
    d = workspace / draft_id
    d.mkdir(parents=True, exist_ok=True)
    (d / "promotion_package.yaml").write_text(yaml.dump(_valid_package()), encoding="utf-8")
    (d / "promotion_orchestration_plan.yaml").write_text(yaml.dump(_valid_plan()), encoding="utf-8")
    (d / "promotion_execution_gate_report.yaml").write_text(yaml.dump(_valid_gate_report()), encoding="utf-8")
    (d / "promotion_execution_packet.yaml").write_text(yaml.dump(_valid_execution_packet(token)), encoding="utf-8")


def _patch_workspace(monkeypatch, tmp_path):
    import alters_lab.api.promotion_live_execution as mod
    monkeypatch.setattr(mod, "get_promotion_live_execution_workspace", lambda: tmp_path / "drafts")


# --- health ---


def test_health():
    r = client.get("/promotion-live-execution/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["component"] == "promotion-live-execution"
    assert body["mode"] == "controlled_live_runtime"
    assert body["default_live_execution_enabled"] is False
    assert body["provider_used"] is False
    assert body["database_added"] is False
    assert body["frontend_added"] is False


# --- dry_run mode ---


def test_dry_run_missing_inputs_returns_404(monkeypatch, tmp_path):
    _patch_workspace(monkeypatch, tmp_path)
    r = client.post("/promotion-live-execution/nonexistent/run", json={"mode": "dry_run"})
    assert r.status_code in (400, 404)


def test_dry_run_passes(monkeypatch, tmp_path):
    _patch_workspace(monkeypatch, tmp_path)
    _write_all_inputs(tmp_path / "drafts", "draft_001")
    r = client.post("/promotion-live-execution/draft_001/run", json={
        "mode": "dry_run",
        "final_execution_token": "test-token-123",
    })
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "dry_run_passed"
    assert body["report"]["dry_run_only"] is True
    assert body["report"]["live_execution_performed"] is False


def test_dry_run_without_token_not_rejected(monkeypatch, tmp_path):
    _patch_workspace(monkeypatch, tmp_path)
    _write_all_inputs(tmp_path / "drafts", "draft_001")
    r = client.post("/promotion-live-execution/draft_001/run", json={
        "mode": "dry_run",
    })
    assert r.status_code == 200
    body = r.json()
    assert body["status"] in ("dry_run_passed", "dry_run_failed")
    assert body["report"]["live_execution_performed"] is False


def test_live_without_token_rejected(monkeypatch, tmp_path):
    _patch_workspace(monkeypatch, tmp_path)
    _write_all_inputs(tmp_path / "drafts", "draft_001")
    r = client.post("/promotion-live-execution/draft_001/run", json={
        "mode": "live",
    })
    assert r.status_code == 422


def test_dry_run_save_true_writes_file(monkeypatch, tmp_path):
    _patch_workspace(monkeypatch, tmp_path)
    _write_all_inputs(tmp_path / "drafts", "draft_001")
    r = client.post("/promotion-live-execution/draft_001/run", json={
        "mode": "dry_run",
        "save_report": True,
        "final_execution_token": "tok",
    })
    assert r.status_code == 200
    body = r.json()
    assert body["report_path"] is not None
    assert (tmp_path / "drafts" / "draft_001" / "promotion_live_execution_report.yaml").exists()


def test_dry_run_no_raw_token_in_response(monkeypatch, tmp_path):
    _patch_workspace(monkeypatch, tmp_path)
    _write_all_inputs(tmp_path / "drafts", "draft_001")
    r = client.post("/promotion-live-execution/draft_001/run", json={
        "mode": "dry_run",
        "save_report": True,
        "final_execution_token": "secret",
    })
    body_str = str(r.json())
    assert "secret" not in body_str


def test_dry_run_no_raw_token_in_saved_file(monkeypatch, tmp_path):
    _patch_workspace(monkeypatch, tmp_path)
    _write_all_inputs(tmp_path / "drafts", "draft_001")
    client.post("/promotion-live-execution/draft_001/run", json={
        "mode": "dry_run",
        "save_report": True,
        "final_execution_token": "secret",
    })
    content = (tmp_path / "drafts" / "draft_001" / "promotion_live_execution_report.yaml").read_text()
    assert "secret" not in content


def test_dry_run_no_active_yaml_written(monkeypatch, tmp_path):
    _patch_workspace(monkeypatch, tmp_path)
    _write_all_inputs(tmp_path / "drafts", "draft_001")
    client.post("/promotion-live-execution/draft_001/run", json={
        "mode": "dry_run",
        "save_report": True,
        "final_execution_token": "tok",
    })
    assert not (tmp_path / "alters").exists()


# --- live mode ---


def test_live_mode_rejected_when_not_enabled(monkeypatch, tmp_path):
    _patch_workspace(monkeypatch, tmp_path)
    _write_all_inputs(tmp_path / "drafts", "draft_001")
    r = client.post("/promotion-live-execution/draft_001/run", json={
        "mode": "live",
        "final_execution_token": "test-token-123",
    })
    assert r.status_code == 403
    assert "not enabled" in r.json()["detail"]


def test_live_mode_rejected_without_path_overrides(monkeypatch, tmp_path):
    import alters_lab.api.promotion_live_execution as mod
    monkeypatch.setattr(mod, "LIVE_EXECUTION_ENABLED", True)
    _patch_workspace(monkeypatch, tmp_path)
    _write_all_inputs(tmp_path / "drafts", "draft_001")
    r = client.post("/promotion-live-execution/draft_001/run", json={
        "mode": "live",
        "final_execution_token": "test-token-123",
    })
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "rejected"
    assert any("path_overrides" in e for e in body["report"]["blocking_failures"])


def test_live_mode_requires_token(monkeypatch, tmp_path):
    _patch_workspace(monkeypatch, tmp_path)
    r = client.post("/promotion-live-execution/draft_001/run", json={
        "mode": "live",
    })
    assert r.status_code == 422


def test_save_report_requires_token(monkeypatch, tmp_path):
    _patch_workspace(monkeypatch, tmp_path)
    r = client.post("/promotion-live-execution/draft_001/run", json={
        "mode": "dry_run",
        "save_report": True,
    })
    assert r.status_code == 422


def test_rejects_invalid_mode(monkeypatch, tmp_path):
    _patch_workspace(monkeypatch, tmp_path)
    r = client.post("/promotion-live-execution/draft_001/run", json={
        "mode": "evil",
    })
    assert r.status_code == 422


# --- list ---


def test_list_returns_empty(monkeypatch, tmp_path):
    _patch_workspace(monkeypatch, tmp_path)
    r = client.get("/promotion-live-execution/list")
    assert r.status_code == 200
    assert r.json()["count"] == 0


def test_list_returns_metadata_only(monkeypatch, tmp_path):
    _patch_workspace(monkeypatch, tmp_path)
    _write_all_inputs(tmp_path / "drafts", "draft_001")
    client.post("/promotion-live-execution/draft_001/run", json={"mode": "dry_run"})
    r = client.get("/promotion-live-execution/list")
    assert r.json()["count"] == 1
    assert "dry_run_passed" not in str(r.json())


# --- extra field rejection ---


def test_rejects_extra_fields():
    r = client.post("/promotion-live-execution/draft_001/run", json={
        "mode": "dry_run", "provider": {"name": "openai"},
    })
    assert r.status_code == 422


def test_rejects_calibration():
    r = client.post("/promotion-live-execution/draft_001/run", json={
        "mode": "dry_run", "calibration": {"score": 0.9},
    })
    assert r.status_code == 422


# --- no forbidden routers ---


def test_no_forbidden_routers():
    from alters_lab.main import app as _app
    routes = [route.path for route in _app.routes]
    for forbidden in ["dialogue", "calibration", "archive"]:
        for route in routes:
            if forbidden in route.lower() and route != "/health" and not route.startswith("/alter-dialogue") and not route.startswith("/calibration-loop") and not route.startswith("/archive-mechanism") and not route.startswith("/provider-dialogue") and not route.startswith("/p6-data-retention"):
                pytest.fail(f"Unexpected route: {route}")


# --- no provider imports ---


def test_no_provider_imports():
    import ast
    from pathlib import Path
    api_dir = Path(__file__).resolve().parent.parent / "src" / "alters_lab" / "api"
    for py_file in api_dir.glob("promotion_live_execution.py"):
        tree = ast.parse(py_file.read_text())
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                mod = getattr(node, "module", None) or ""
                names = [a.name for a in getattr(node, "names", [])]
                for forbidden in ["openai", "anthropic", "openrouter", "litellm", "langchain", "crewai"]:
                    if forbidden in mod or any(forbidden in n for n in names):
                        pytest.fail(f"Provider import found: {forbidden}")


# --- route inventory ---


def test_route_inventory():
    from alters_lab.main import app as _app
    routes = sorted(route.path for route in _app.routes)
    assert "/promotion-live-execution/health" in routes
    assert "/promotion-live-execution/{draft_id}/run" in routes
    assert "/promotion-live-execution/list" in routes
    assert "/promotion-execution-gate/health" in routes
    assert "/promotion-orchestration/health" in routes
    assert "/branches/persist" in routes
    assert "/alters/persist-batch" in routes
