"""Tests for Phase 4 Closeout API."""

from __future__ import annotations

import json

from fastapi.testclient import TestClient

from alters_lab.main import app

client = TestClient(app)


def test_health_endpoint_ok():
    r = client.get("/phase4-closeout/health")
    assert r.status_code == 200
    assert r.json()["mode"] == "read_only_phase4_closeout"


def test_report_endpoint_read_only():
    r = client.get("/phase4-closeout/report")
    assert r.status_code == 200
    data = r.json()
    assert data["report"]["boundary_confirmations"]["active_yaml_modified"] is False
    assert data["report"]["boundary_confirmations"]["rubric_modified"] is False


def test_evidence_endpoint_reads_existing_evidence_only(tmp_path, monkeypatch):
    harness = tmp_path / "docs" / "harness"
    harness.mkdir(parents=True)
    evidence_path = harness / "PHASE4_CLOSEOUT_EVIDENCE.json"
    evidence_path.write_text(json.dumps({"status": "PASS"}), encoding="utf-8")
    monkeypatch.setattr("alters_lab.api.phase4_closeout.get_repo_root", lambda: tmp_path)
    r = client.get("/phase4-closeout/evidence")
    assert r.status_code == 200
    assert r.json()["evidence"]["status"] == "PASS"


def test_evidence_endpoint_404_when_missing(tmp_path, monkeypatch):
    monkeypatch.setattr("alters_lab.api.phase4_closeout.get_repo_root", lambda: tmp_path)
    r = client.get("/phase4-closeout/evidence")
    assert r.status_code == 404


def test_no_frontend_live_execution_route_exposed_from_p4_paths():
    routes = sorted(route.path for route in app.routes)
    assert "/frontend/live-execution" not in routes
    assert "/checkpoint-regeneration/execute" not in routes
    assert "/rubric-delta/apply" not in routes
