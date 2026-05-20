"""Tests for P4-M6 Archive Mechanism API."""

from __future__ import annotations

from fastapi.testclient import TestClient

from alters_lab.main import app

client = TestClient(app)


def _write_source(tmp_path):
    path = tmp_path / "alters" / "current" / "snapshot.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("snapshot: ok\n", encoding="utf-8")


def test_health():
    r = client.get("/archive-mechanism/health")
    assert r.status_code == 200
    assert r.json()["active_write_allowed"] is False


def test_plan_archive_read_only(tmp_path, monkeypatch):
    monkeypatch.setattr("alters_lab.api.archive_mechanism._repo_root", lambda: tmp_path)
    _write_source(tmp_path)
    r = client.post("/archive-mechanism/plan", json={"reason": "before future write"})
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "planned"
    assert data["archive_path"] is None
    assert not (tmp_path / "alters" / "archive").exists()


def test_create_archive_is_explicit_request_only(tmp_path, monkeypatch):
    monkeypatch.setattr("alters_lab.api.archive_mechanism._repo_root", lambda: tmp_path)
    _write_source(tmp_path)
    r = client.post("/archive-mechanism/create", json={"reason": "explicit archive"})
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "created"
    assert data["archive_path"].startswith(str(tmp_path))


def test_create_rejects_auto_archive(tmp_path, monkeypatch):
    monkeypatch.setattr("alters_lab.api.archive_mechanism._repo_root", lambda: tmp_path)
    r = client.post("/archive-mechanism/create", json={"reason": "x", "auto_archive": True})
    assert r.status_code == 422


def test_list_archives(tmp_path, monkeypatch):
    monkeypatch.setattr("alters_lab.api.archive_mechanism._repo_root", lambda: tmp_path)
    r = client.get("/archive-mechanism/list")
    assert r.status_code == 200
    assert r.json()["count"] == 0
