from __future__ import annotations

import json

from fastapi.testclient import TestClient

from alters_lab.main import app
from alters_lab.services.evidence_reports import evidence_paths

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
    if data["exists"]:
        assert "line_count" in data
        assert "contains_sealed_baseline" in data
        assert "contains_final_gate_pass" in data


# --- Status endpoint ---


def test_evidence_status():
    r = client.get("/evidence/status")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] in ("PASS", "WARN", "ERROR")
    assert data["read_only"] is True
    assert "day30_demo" in data
    assert "active_yaml_validation" in data
    assert "phase1_closeout" in data
    assert "boundary_confirmations" in data


def test_evidence_status_boundary_confirmations():
    r = client.get("/evidence/status")
    data = r.json()
    bc = data["boundary_confirmations"]
    assert bc["no_provider_imports"] is True
    assert bc["no_database_imports"] is True
    assert bc["no_frontend_code"] is True
    assert bc["no_env_file"] is True
    assert bc["no_dialogue_runtime"] is True
    assert bc["no_calibration_runtime"] is True
    assert bc["no_archive_runtime"] is True
    assert bc["no_score_yaml"] is True
    assert bc["no_archive_folders"] is True
    assert bc["no_active_yaml_mutation"] is True
    assert bc["read_only_validation_enforced"] is True


def test_evidence_status_pass_when_all_present():
    r = client.get("/evidence/status")
    data = r.json()
    paths = evidence_paths()
    all_exist = all(p.exists() for p in paths.values())
    if all_exist:
        assert data["status"] == "PASS"


# --- Active YAML validation details ---


def test_evidence_active_yaml_validation_fields():
    r = client.get("/evidence/active-yaml-validation")
    data = r.json()
    if data["status"] == "ok":
        assert data.get("selected_branch") == "branch_D"
        assert data.get("primary_candidate") == "branch_D"
        assert data.get("calibration_ready") is False


# --- Phase 1 closeout metadata ---


def test_evidence_phase1_closeout_metadata():
    r = client.get("/evidence/phase1-closeout")
    data = r.json()
    if data["exists"]:
        assert isinstance(data["line_count"], int)
        assert isinstance(data["contains_sealed_baseline"], bool)
        assert isinstance(data["contains_final_gate_pass"], bool)


# --- No full YAML/markdown exposure ---


def test_evidence_endpoints_do_not_expose_full_content():
    for endpoint in ("/evidence/status", "/evidence/day30-demo",
                     "/evidence/active-yaml-validation", "/evidence/phase1-closeout"):
        r = client.get(endpoint)
        data = r.json()
        text = json.dumps(data)
        assert "snapshot:" not in text.lower() or "snapshot_phase" in text
        assert len(text) < 10000, f"{endpoint} returns suspiciously large payload"


# --- Read-only safety ---


def test_api_does_not_modify_active_yaml():
    from pathlib import Path
    root = Path(__file__).resolve().parents[3]
    yaml_files = list(root.glob("alters/current/**/*.yaml"))
    snapshots_before = {f: f.stat().st_mtime for f in yaml_files}
    client.get("/evidence/status")
    client.get("/evidence/reports")
    client.get("/evidence/day30-demo")
    client.get("/evidence/active-yaml-validation")
    client.get("/evidence/phase1-closeout")
    for f in yaml_files:
        assert f.stat().st_mtime == snapshots_before[f], f"{f.name} was modified"


def test_no_score_yaml_created():
    from pathlib import Path
    root = Path(__file__).resolve().parents[3]
    score_files = list(root.glob("**/score_*.yaml"))
    assert len(score_files) == 0, f"Found unexpected score YAML: {score_files}"


def test_no_archive_folders_created():
    from pathlib import Path
    root = Path(__file__).resolve().parents[3]
    archive_folders = [d for d in root.glob("alters/archive/20*") if d.is_dir()]
    assert len(archive_folders) == 0, f"Found unexpected archive folders: {archive_folders}"


# --- 404 for non-existent routes ---


def test_evidence_nonexistent_endpoint_returns_404():
    r = client.get("/evidence/nonexistent")
    assert r.status_code == 404
