from __future__ import annotations

from fastapi.testclient import TestClient

from alters_lab.main import app

client = TestClient(app)


# --- Health ---


def test_evidence_health():
    r = client.get("/evidence/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert data["component"] == "evidence-reports"
    assert data["mode"] == "read_only"


# --- Reports list ---


def test_evidence_reports_list():
    r = client.get("/evidence/reports")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert data["read_only"] is True
    assert isinstance(data["reports"], list)
    assert data["count"] == len(data["reports"])


def test_evidence_reports_list_has_expected_keys():
    r = client.get("/evidence/reports")
    data = r.json()
    keys = {report["key"] for report in data["reports"]}
    assert "day30_demo" in keys
    assert "active_yaml_validation" in keys
    assert "phase1_closeout" in keys


def test_evidence_reports_entries_have_required_fields():
    r = client.get("/evidence/reports")
    data = r.json()
    for report in data["reports"]:
        assert "key" in report
        assert "path" in report
        assert "exists" in report
        assert "format" in report
        assert report["format"] in ("json", "markdown")


# --- Single report queries ---


def test_evidence_day30_demo():
    r = client.get("/evidence/day30-demo")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] in ("ok", "MISSING", "ERROR")
    assert isinstance(data["exists"], bool)


def test_evidence_active_yaml_validation():
    r = client.get("/evidence/active-yaml-validation")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] in ("ok", "MISSING", "ERROR")
    assert isinstance(data["exists"], bool)


def test_evidence_phase1_closeout():
    r = client.get("/evidence/phase1-closeout")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] in ("ok", "MISSING")
    assert isinstance(data["exists"], bool)


def test_evidence_status():
    r = client.get("/evidence/status")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert data["read_only"] is True
    assert "day30_demo" in data
    assert "active_yaml_validation" in data
    assert "phase1_closeout" in data


# --- 404 for non-existent routes ---


def test_evidence_nonexistent_endpoint_returns_404():
    r = client.get("/evidence/nonexistent")
    assert r.status_code == 404
