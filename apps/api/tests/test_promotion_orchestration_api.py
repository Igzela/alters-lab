"""API tests for promotion orchestration plan."""

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


def _patch_workspace(monkeypatch, tmp_path):
    import alters_lab.api.promotion_orchestration as mod
    monkeypatch.setattr(mod, "get_promotion_orchestration_workspace", lambda: tmp_path / "drafts")


# --- health ---


def test_orchestration_health():
    r = client.get("/promotion-orchestration/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["component"] == "promotion-orchestration"
    assert body["mode"] == "plan_only"
    assert body["active_execution_allowed"] is False
    assert body["provider_used"] is False


# --- plan endpoint ---


def test_plan_missing_package_returns_404(monkeypatch, tmp_path):
    _patch_workspace(monkeypatch, tmp_path)
    r = client.post("/promotion-orchestration/nonexistent/plan", json={})
    assert r.status_code == 404


def test_plan_path_traversal_rejected(monkeypatch, tmp_path):
    _patch_workspace(monkeypatch, tmp_path)
    r = client.post("/promotion-orchestration/../etc/passwd/plan", json={})
    assert r.status_code in (400, 404, 422)


def test_plan_save_false_writes_nothing(monkeypatch, tmp_path):
    _patch_workspace(monkeypatch, tmp_path)
    _write_promotion_package(tmp_path / "drafts", "draft_001", _valid_promotion_package())
    r = client.post("/promotion-orchestration/draft_001/plan", json={"save_plan": False})
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "plan_generated"
    assert body["plan_path"] is None
    assert not (tmp_path / "drafts" / "draft_001" / "promotion_orchestration_plan.yaml").exists()


def test_plan_returns_active_execution_false(monkeypatch, tmp_path):
    _patch_workspace(monkeypatch, tmp_path)
    _write_promotion_package(tmp_path / "drafts", "draft_001", _valid_promotion_package())
    r = client.post("/promotion-orchestration/draft_001/plan", json={})
    assert r.status_code == 200
    body = r.json()
    assert body["plan"]["active_execution_allowed"] is False
    assert body["plan"]["requires_human_final_approval"] is True


def test_plan_returns_steps_targeting_allowed_apis(monkeypatch, tmp_path):
    _patch_workspace(monkeypatch, tmp_path)
    _write_promotion_package(tmp_path / "drafts", "draft_001", _valid_promotion_package())
    r = client.post("/promotion-orchestration/draft_001/plan", json={})
    body = r.json()
    target_apis = [s["target_api"] for s in body["plan"]["steps"]]
    assert "/branches/persist" in target_apis
    assert "/alters/persist-batch" in target_apis


def test_plan_save_true_requires_token(monkeypatch, tmp_path):
    _patch_workspace(monkeypatch, tmp_path)
    _write_promotion_package(tmp_path / "drafts", "draft_001", _valid_promotion_package())
    r = client.post("/promotion-orchestration/draft_001/plan", json={"save_plan": True})
    assert r.status_code == 422


def test_plan_save_true_writes_file(monkeypatch, tmp_path):
    _patch_workspace(monkeypatch, tmp_path)
    _write_promotion_package(tmp_path / "drafts", "draft_001", _valid_promotion_package())
    r = client.post("/promotion-orchestration/draft_001/plan", json={
        "save_plan": True, "approval_token": "tok",
    })
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "plan_saved"
    assert body["plan_path"] is not None
    assert (tmp_path / "drafts" / "draft_001" / "promotion_orchestration_plan.yaml").exists()


def test_plan_no_raw_token_in_response(monkeypatch, tmp_path):
    _patch_workspace(monkeypatch, tmp_path)
    _write_promotion_package(tmp_path / "drafts", "draft_001", _valid_promotion_package())
    r = client.post("/promotion-orchestration/draft_001/plan", json={
        "save_plan": True, "approval_token": "secret",
    })
    body_str = str(r.json())
    assert "secret" not in body_str


def test_plan_no_raw_token_in_saved_file(monkeypatch, tmp_path):
    _patch_workspace(monkeypatch, tmp_path)
    _write_promotion_package(tmp_path / "drafts", "draft_001", _valid_promotion_package())
    client.post("/promotion-orchestration/draft_001/plan", json={
        "save_plan": True, "approval_token": "secret",
    })
    content = (tmp_path / "drafts" / "draft_001" / "promotion_orchestration_plan.yaml").read_text()
    assert "secret" not in content


def test_plan_no_active_yaml_written(monkeypatch, tmp_path):
    _patch_workspace(monkeypatch, tmp_path)
    _write_promotion_package(tmp_path / "drafts", "draft_001", _valid_promotion_package())
    client.post("/promotion-orchestration/draft_001/plan", json={
        "save_plan": True, "approval_token": "tok",
    })
    assert not (tmp_path / "alters").exists()


# --- list ---


def test_list_returns_empty(monkeypatch, tmp_path):
    _patch_workspace(monkeypatch, tmp_path)
    r = client.get("/promotion-orchestration/list")
    assert r.status_code == 200
    assert r.json()["count"] == 0


def test_list_returns_metadata_only(monkeypatch, tmp_path):
    _patch_workspace(monkeypatch, tmp_path)
    _write_promotion_package(tmp_path / "drafts", "draft_001", _valid_promotion_package())
    r = client.get("/promotion-orchestration/list")
    assert r.json()["count"] == 1
    assert "promotion_plan" not in str(r.json())


# --- extra field rejection ---


def test_plan_rejects_extra_fields():
    r = client.post("/promotion-orchestration/draft_001/plan", json={
        "save_plan": False, "provider": {"name": "openai"},
    })
    assert r.status_code == 422


def test_plan_rejects_calibration():
    r = client.post("/promotion-orchestration/draft_001/plan", json={
        "save_plan": False, "calibration": {"score": 0.9},
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
    for py_file in api_dir.glob("promotion_orchestration.py"):
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
    service_file = Path(__file__).resolve().parent.parent / "src" / "alters_lab" / "services" / "promotion_orchestration.py"
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
    assert "/promotion-orchestration/health" in routes
    assert "/promotion-orchestration/{draft_id}/plan" in routes
    assert "/promotion-orchestration/list" in routes
    assert "/draft-review/{draft_id}/review" in routes
    assert "/generation-drafts/preview" in routes
    assert "/branches/persist" in routes
    assert "/alters/persist-batch" in routes
