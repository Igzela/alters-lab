"""Tests for P5-M3 Provider-backed Alter Dialogue API routes."""

from __future__ import annotations

import os

from fastapi.testclient import TestClient

from alters_lab.main import app

client = TestClient(app)


def test_health():
    original = os.environ.get("ALTERS_PROVIDER_MODE")
    try:
        os.environ["ALTERS_PROVIDER_MODE"] = "mock"
        r = client.get("/provider-dialogue/health")
        assert r.status_code == 200
        data = r.json()
        assert data["component"] == "provider-dialogue"
        assert data["provider_mode"] == "mock"
        assert data["default_persist"] is False
    finally:
        if original is not None:
            os.environ["ALTERS_PROVIDER_MODE"] = original


def test_mock_reply(tmp_path, monkeypatch):
    original = os.environ.get("ALTERS_PROVIDER_MODE")
    try:
        os.environ["ALTERS_PROVIDER_MODE"] = "mock"
        monkeypatch.setattr("alters_lab.services.provider_dialogue._get_repo_root", lambda: tmp_path)
        alters_dir = tmp_path / "alters" / "current" / "alters"
        alters_dir.mkdir(parents=True)
        (alters_dir / "alter_A.yaml").write_text("id: alter_A\nbranch_ref: branch_A\n", encoding="utf-8")
        r = client.post("/provider-dialogue/alter_A/reply", json={
            "user_message": "Hello alter A",
        })
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "mock_response"
        assert data["alter_id"] == "alter_A"
        assert data["persisted"] is False
        assert data["session_path"] is None
    finally:
        if original is not None:
            os.environ["ALTERS_PROVIDER_MODE"] = original


def test_invalid_alter_id():
    r = client.post("/provider-dialogue/alter_Z/reply", json={
        "user_message": "Hello",
    })
    assert r.status_code == 400


def test_save_session_false(tmp_path, monkeypatch):
    original = os.environ.get("ALTERS_PROVIDER_MODE")
    try:
        os.environ["ALTERS_PROVIDER_MODE"] = "mock"
        monkeypatch.setattr("alters_lab.services.provider_dialogue._get_repo_root", lambda: tmp_path)
        alters_dir = tmp_path / "alters" / "current" / "alters"
        alters_dir.mkdir(parents=True)
        (alters_dir / "alter_A.yaml").write_text("id: alter_A\nbranch_ref: branch_A\n", encoding="utf-8")
        r = client.post("/provider-dialogue/alter_A/reply", json={
            "user_message": "test",
            "save_session": False,
        })
        assert r.status_code == 200
        data = r.json()
        assert data["persisted"] is False
        assert data["session_path"] is None
    finally:
        if original is not None:
            os.environ["ALTERS_PROVIDER_MODE"] = original


def test_save_session_true(tmp_path, monkeypatch):
    original = os.environ.get("ALTERS_PROVIDER_MODE")
    try:
        os.environ["ALTERS_PROVIDER_MODE"] = "mock"
        monkeypatch.setattr("alters_lab.services.provider_dialogue._get_repo_root", lambda: tmp_path)
        alters_dir = tmp_path / "alters" / "current" / "alters"
        alters_dir.mkdir(parents=True)
        (alters_dir / "alter_A.yaml").write_text("id: alter_A\nbranch_ref: branch_A\n", encoding="utf-8")
        r = client.post("/provider-dialogue/alter_A/reply", json={
            "user_message": "test",
            "save_session": True,
        })
        assert r.status_code == 200
        data = r.json()
        assert data["persisted"] is True
        assert data["session_path"] is not None
        assert "alters/product/sessions" in data["session_path"]
    finally:
        if original is not None:
            os.environ["ALTERS_PROVIDER_MODE"] = original


def test_no_api_key_leakage(tmp_path, monkeypatch):
    original_mode = os.environ.get("ALTERS_PROVIDER_MODE")
    original_key = os.environ.get("ALTERS_PROVIDER_API_KEY")
    try:
        os.environ["ALTERS_PROVIDER_MODE"] = "mock"
        os.environ["ALTERS_PROVIDER_API_KEY"] = "sk-test-secret"
        monkeypatch.setattr("alters_lab.services.provider_dialogue._get_repo_root", lambda: tmp_path)
        alters_dir = tmp_path / "alters" / "current" / "alters"
        alters_dir.mkdir(parents=True)
        (alters_dir / "alter_A.yaml").write_text("id: alter_A\nbranch_ref: branch_A\n", encoding="utf-8")
        r = client.post("/provider-dialogue/alter_A/reply", json={
            "user_message": "test",
            "save_session": True,
        })
        assert r.status_code == 200
        data = r.json()
        assert "sk-" not in data["reply_text"]
    finally:
        if original_mode is not None:
            os.environ["ALTERS_PROVIDER_MODE"] = original_mode
        else:
            os.environ.pop("ALTERS_PROVIDER_MODE", None)
        if original_key is not None:
            os.environ["ALTERS_PROVIDER_API_KEY"] = original_key
        else:
            os.environ.pop("ALTERS_PROVIDER_API_KEY", None)


def test_route_inventory():
    routes = sorted(route.path for route in app.routes)
    assert "/provider-dialogue/health" in routes
    assert "/provider-dialogue/{alter_id}/reply" in routes
