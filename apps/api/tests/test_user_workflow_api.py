"""Tests for P5-M6 User Workflow Integration API routes."""

from __future__ import annotations

from fastapi.testclient import TestClient

from alters_lab.main import app

client = TestClient(app)


def test_health():
    r = client.get("/user-workflow/health")
    assert r.status_code == 200
    data = r.json()
    assert data["component"] == "user-workflow"
    assert data["read_only"] is True


def test_state():
    r = client.get("/user-workflow/state")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert data["read_only"] is True
    assert isinstance(data["available_alters"], list)
    assert data["provider_status"] == "mock_default"
    assert isinstance(data["last_reality_scores"], list)


def test_run_summary(tmp_path, monkeypatch):
    monkeypatch.setattr("alters_lab.services.user_workflow._get_repo_root", lambda: tmp_path)
    r = client.post("/user-workflow/run-summary", json={
        "action": "test_action",
        "alter_id": "alter_A",
        "notes": "test note",
    })
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "saved"
    assert data["run_id"] is not None
    assert data["run_path"] is not None
    assert data["active_yaml_modified"] is False


def test_no_active_yaml_diff(tmp_path, monkeypatch):
    monkeypatch.setattr("alters_lab.services.user_workflow._get_repo_root", lambda: tmp_path)
    client.post("/user-workflow/run-summary", json={
        "action": "test",
        "alter_id": "alter_A",
    })
    assert not (tmp_path / "alters" / "current").exists()


def test_route_inventory():
    routes = sorted(route.path for route in app.routes)
    assert "/user-workflow/health" in routes
    assert "/user-workflow/state" in routes
    assert "/user-workflow/run-summary" in routes
