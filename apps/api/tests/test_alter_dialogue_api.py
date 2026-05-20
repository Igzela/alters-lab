"""Tests for Alter Dialogue Runtime API (P4-M1)."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from alters_lab.main import app

client = TestClient(app)


def test_health():
    r = client.get("/alter-dialogue/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert data["component"] == "alter-dialogue"
    assert data["mode"] == "read_only_no_provider"
    assert data["provider_used"] is False
    assert data["active_write_allowed"] is False


def test_list_alters():
    r = client.get("/alter-dialogue/alters")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert data["count"] == 4
    ids = {a["alter_id"] for a in data["alters"]}
    assert ids == {"alter_A", "alter_B", "alter_C", "alter_D"}


def test_list_alters_no_full_yaml():
    r = client.get("/alter-dialogue/alters")
    data = r.json()
    for a in data["alters"]:
        assert "source_branch" not in a
        assert "life_state" not in a
        assert "tradeoffs" not in a


def test_get_context():
    r = client.get("/alter-dialogue/alter_A/context")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "context_ready"
    assert data["alter_id"] == "alter_A"
    ctx = data["dialogue_context"]
    assert ctx["alter_id"] == "alter_A"
    assert ctx["core_stance"]
    assert len(ctx["allowed_scope"]) > 0
    assert len(ctx["forbidden_scope"]) > 0


def test_get_context_invalid_alter():
    r = client.get("/alter-dialogue/alter_E/context")
    assert r.status_code == 400


def test_get_context_path_traversal():
    r = client.get("/alter-dialogue/alter_A/../etc/context")
    assert r.status_code in (400, 404)


def test_get_context_missing_alter(tmp_path, monkeypatch):
    monkeypatch.setattr("alters_lab.api.alter_dialogue._repo_root", lambda: tmp_path)
    r = client.get("/alter-dialogue/alter_A/context")
    assert r.status_code == 404


def test_prompt():
    r = client.post(
        "/alter-dialogue/alter_A/prompt",
        json={"user_message": "Hello alter"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "prompt_packet_ready"
    assert data["alter_id"] == "alter_A"
    assert data["prompt_packet"]["provider_ready"] is False
    assert data["prompt_packet"]["persistence_policy"] == "read_only_no_active_yaml_write"
    assert data["prompt_packet"]["full_context_injected"] is True
    assert data["prompt_packet"]["context_injection_policy"] == "full_alter_yaml_required"
    assert data["prompt_packet"]["full_alter_yaml"]["id"] == "alter_A"
    assert "personality_drift" in data["prompt_packet"]["full_alter_yaml"]
    assert "Hello alter" in data["prompt_packet"]["user_message"]


def test_prompt_no_context():
    r = client.post(
        "/alter-dialogue/alter_A/prompt",
        json={"user_message": "Hello", "include_context_packet": False},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "context_ready"
    assert data["prompt_packet"] is None


def test_prompt_invalid_alter():
    r = client.post(
        "/alter-dialogue/alter_E/prompt",
        json={"user_message": "Hello"},
    )
    assert r.status_code == 400


def test_prompt_empty_message():
    r = client.post(
        "/alter-dialogue/alter_A/prompt",
        json={"user_message": ""},
    )
    assert r.status_code == 422


def test_prompt_extra_fields_rejected():
    r = client.post(
        "/alter-dialogue/alter_A/prompt",
        json={"user_message": "Hello", "provider": "openai"},
    )
    assert r.status_code == 422


def test_prompt_rejects_model_field():
    r = client.post(
        "/alter-dialogue/alter_A/prompt",
        json={"user_message": "Hello", "model": "gpt-4"},
    )
    assert r.status_code == 422


def test_prompt_rejects_runtime_field():
    r = client.post(
        "/alter-dialogue/alter_A/prompt",
        json={"user_message": "Hello", "runtime": True},
    )
    assert r.status_code == 422


def test_prompt_rejects_calibration_field():
    r = client.post(
        "/alter-dialogue/alter_A/prompt",
        json={"user_message": "Hello", "calibration": True},
    )
    assert r.status_code == 422


def test_prompt_rejects_write_field():
    r = client.post(
        "/alter-dialogue/alter_A/prompt",
        json={"user_message": "Hello", "write_active_yaml": True},
    )
    assert r.status_code == 422


def test_prompt_rejects_archive_field():
    r = client.post(
        "/alter-dialogue/alter_A/prompt",
        json={"user_message": "Hello", "archive": True},
    )
    assert r.status_code == 422


def test_route_inventory():
    routes = sorted(route.path for route in app.routes)
    assert "/alter-dialogue/health" in routes
    assert "/alter-dialogue/alters" in routes
    assert "/alter-dialogue/{alter_id}/context" in routes
    assert "/alter-dialogue/{alter_id}/prompt" in routes
    assert "/phase3-closeout/report" in routes


def test_no_active_yaml_written():
    snapshot_path = Path("alters/current/snapshot.yaml")
    branches_path = Path("alters/current/branches.yaml")
    snap_before = snapshot_path.read_text() if snapshot_path.exists() else ""
    branches_before = branches_path.read_text() if branches_path.exists() else ""

    client.get("/alter-dialogue/health")
    client.get("/alter-dialogue/alters")
    client.get("/alter-dialogue/alter_A/context")
    client.post("/alter-dialogue/alter_A/prompt", json={"user_message": "test"})

    snap_after = snapshot_path.read_text() if snapshot_path.exists() else ""
    branches_after = branches_path.read_text() if branches_path.exists() else ""
    assert snap_before == snap_after
    assert branches_before == branches_after


def test_no_provider_imports():
    import alters_lab.api.alter_dialogue as mod
    import alters_lab.services.alter_dialogue as svc
    source_api = mod.__file__
    source_svc = svc.__file__
    for path in [source_api, source_svc]:
        with open(path) as f:
            content = f.read()
        for pattern in ["openai", "anthropic", "openrouter", "litellm", "langchain", "crewai"]:
            assert pattern not in content.lower(), f"{pattern} found in {path}"


def test_no_persist_or_live_execution_calls():
    import alters_lab.services.alter_dialogue as svc
    source = open(svc.__file__).read()
    for pattern in ["write_.*with_audit", "execute_promotion_live", "run_live_execution_gate"]:
        assert pattern not in source, f"{pattern} found in alter_dialogue service"


def test_prompt_endpoint_no_write(monkeypatch, tmp_path):
    monkeypatch.setattr("alters_lab.api.alter_dialogue._repo_root", lambda: tmp_path)
    # Create a valid alter in tmp_path
    alters_dir = tmp_path / "alters" / "current" / "alters"
    alters_dir.mkdir(parents=True)
    import yaml
    valid_alter = {
        "id": "alter_A",
        "branch_ref": "branch_A",
        "label": "Test",
        "voice": {"core_stance": "Test stance"},
        "source_refs": {
            "snapshot_ref": "alters/current/snapshot.yaml",
            "branches_ref": "alters/current/branches.yaml",
            "rubric_ref": "alters/calibration/rubric.yaml",
        },
        "quality_status": {"human_confirmed": True, "active": True},
    }
    (alters_dir / "alter_A.yaml").write_text(yaml.dump(valid_alter))

    files_before = list(tmp_path.rglob("*"))
    r = client.post(
        "/alter-dialogue/alter_A/prompt",
        json={"user_message": "test"},
    )
    assert r.status_code == 200
    files_after = list(tmp_path.rglob("*"))
    # No new files should be created (only reads)
    assert len(files_after) == len(files_before)
