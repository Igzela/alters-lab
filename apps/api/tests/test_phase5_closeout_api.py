"""Tests for P5-M7 Phase 5 Closeout API routes."""

from __future__ import annotations

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


def test_evidence():
    r = client.get("/phase5-closeout/evidence")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert "evidence_path" in data


def test_route_inventory():
    routes = sorted(route.path for route in app.routes)
    assert "/phase5-closeout/health" in routes
    assert "/phase5-closeout/report" in routes
    assert "/phase5-closeout/evidence" in routes
