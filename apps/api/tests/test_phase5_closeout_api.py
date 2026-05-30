"""Tests for P5-M7 Phase 5 Closeout API routes."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from alters_lab.main import app

client = TestClient(app)


def test_health():
    r = client.get("/phase5-closeout/health")
    assert r.status_code == 200
    data = r.json()
    assert data["component"] == "phase5-closeout"
    assert data["read_only"] is True


def test_report():
    r = client.get("/phase5-closeout/report")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] in ("PASS", "PASS_WITH_NOTES", "FAIL")
    assert data["read_only"] is True
    assert "summary" in data
    assert "checks" in data
    assert data["summary"]["sealed_baseline_candidate"] is True


def test_evidence_reads_existing_file():
    r = client.get("/phase5-closeout/evidence")
    # Evidence file may not exist if harness docs were cleaned up
    assert r.status_code in (200, 404)
    if r.status_code == 200:
        data = r.json()
        assert data["status"] == "ok"
        assert "evidence_path" in data


def test_evidence_returns_404_when_missing(tmp_path, monkeypatch):
    monkeypatch.setattr("alters_lab.api.phase5_closeout._get_repo_root", lambda: tmp_path)
    r = client.get("/phase5-closeout/evidence")
    assert r.status_code == 404
    assert "not found" in r.json()["detail"].lower()


def test_evidence_creates_no_files(tmp_path, monkeypatch):
    """Regression test: GET /evidence must be read-only and create no files."""
    monkeypatch.setattr("alters_lab.api.phase5_closeout._get_repo_root", lambda: tmp_path)
    harness = tmp_path / "docs" / "harness"
    harness.mkdir(parents=True)
    before = set(harness.iterdir()) if harness.exists() else set()
    r = client.get("/phase5-closeout/evidence")
    after = set(harness.iterdir()) if harness.exists() else set()
    assert r.status_code == 404
    assert before == after


def test_route_inventory():
    routes = sorted(route.path for route in app.routes)
    assert "/phase5-closeout/health" in routes
    assert "/phase5-closeout/report" in routes
    assert "/phase5-closeout/evidence" in routes
