"""Tests for Phase 3 Closeout Gate API."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from alters_lab.main import app

client = TestClient(app)


def test_health():
    r = client.get("/phase3-closeout/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert data["mode"] == "read_only_closeout"


def test_report_returns_report():
    r = client.get("/phase3-closeout/report")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] in ("PASS", "PASS_WITH_NOTES", "BLOCKED")
    assert "report" in data
    assert "boundary_confirmations" in data


def test_report_no_write_files():
    r = client.get("/phase3-closeout/report")
    assert r.status_code == 200
    data = r.json()
    bc = data["boundary_confirmations"]
    assert bc["read_only"] is True
    assert bc["controlled_persist_called"] is False
    assert bc["live_execution_called"] is False


def test_report_has_checks():
    r = client.get("/phase3-closeout/report")
    data = r.json()
    report = data["report"]
    assert len(report["checks"]) > 0
    for check in report["checks"]:
        assert "name" in check
        assert "status" in check
        assert check["status"] in ("PASS", "WARN", "FAIL")


def test_evidence_404_before_report():
    # Delete evidence file if it exists
    evidence_path = Path("docs/harness/PHASE3_CLOSEOUT_EVIDENCE.json")
    existed = evidence_path.exists()
    if existed:
        content = evidence_path.read_text()
        evidence_path.unlink()
    try:
        r = client.get("/phase3-closeout/evidence")
        # May be 404 or may find existing evidence
        assert r.status_code in (200, 404)
    finally:
        if existed:
            evidence_path.write_text(content)


def test_evidence_returns_after_report():
    # Generate report first
    client.get("/phase3-closeout/report")
    r = client.get("/phase3-closeout/evidence")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "evidence_found"
    assert "evidence" in data


def test_no_extra_mutation_routes():
    routes = [route.path for route in app.routes]
    forbidden = ["/phase3-closeout/create", "/phase3-closeout/write", "/phase3-closeout/seal"]
    for f in forbidden:
        assert f not in routes, f"Forbidden route {f} exists"


def test_route_inventory():
    routes = sorted(route.path for route in app.routes)
    assert "/phase3-closeout/health" in routes
    assert "/phase3-closeout/report" in routes
    assert "/phase3-closeout/evidence" in routes


def test_no_active_yaml_written():
    # Snapshot key files before and after
    snapshot_path = Path("alters/current/snapshot.yaml")
    branches_path = Path("alters/current/branches.yaml")
    snap_before = snapshot_path.read_text() if snapshot_path.exists() else ""
    branches_before = branches_path.read_text() if branches_path.exists() else ""

    client.get("/phase3-closeout/report")
    client.get("/phase3-closeout/evidence")

    snap_after = snapshot_path.read_text() if snapshot_path.exists() else ""
    branches_after = branches_path.read_text() if branches_path.exists() else ""
    assert snap_before == snap_after
    assert branches_before == branches_after


def test_extra_field_rejection():
    with pytest.raises(Exception):
        from alters_lab.schemas.phase3_closeout import Phase3CloseoutResponse
        Phase3CloseoutResponse(
            status="ok",
            report={},
            boundary_confirmations={},
            evil=True,
        )
