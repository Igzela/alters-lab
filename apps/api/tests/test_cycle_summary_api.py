from __future__ import annotations

import hashlib
from pathlib import Path

from fastapi.testclient import TestClient

from alters_lab.loaders import default_project_root
from alters_lab.main import app

client = TestClient(app)


def _project_root() -> Path:
    return default_project_root()


def _hash_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# --- Health ---


def test_cycle_summary_health():
    r = client.get("/cycle-summary/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert data["component"] == "cycle-summary"
    assert data["mode"] == "read_only"


# --- Current ---


def test_current_returns_200():
    r = client.get("/cycle-summary/current")
    assert r.status_code == 200


def test_current_selected_branch():
    r = client.get("/cycle-summary/current")
    data = r.json()
    assert data["summary"]["selected_branch"] == "branch_D"


def test_current_primary_candidate():
    r = client.get("/cycle-summary/current")
    data = r.json()
    assert data["summary"]["primary_candidate"] == "branch_D"


def test_current_branch_count():
    r = client.get("/cycle-summary/current")
    data = r.json()
    assert data["summary"]["branch_count"] == 4


def test_current_validation_ok():
    r = client.get("/cycle-summary/current")
    data = r.json()
    assert data["validation"]["ok"] is True


def test_current_read_only():
    r = client.get("/cycle-summary/current")
    data = r.json()
    assert data["read_only"] is True
    assert data["boundary_confirmations"]["read_only"] is True


# --- Validation ---


def test_validation_ok():
    r = client.get("/cycle-summary/validation")
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert data["artifacts_checked"] == 9


def test_validation_status_pass():
    r = client.get("/cycle-summary/validation")
    data = r.json()
    assert data["status"] == "PASS"


# --- Artifacts ---


def test_artifacts_count():
    r = client.get("/cycle-summary/artifacts")
    assert r.status_code == 200
    data = r.json()
    assert data["count"] == 9
    assert data["read_only"] is True


def test_artifacts_no_full_yaml_content():
    r = client.get("/cycle-summary/artifacts")
    data = r.json()
    for artifact in data["artifacts"]:
        assert "key" in artifact
        assert "path" in artifact
        assert "exists" in artifact
        # Must not contain raw YAML content fields
        assert "content" not in artifact
        assert "yaml" not in artifact


# --- API does not modify active YAML ---


def test_api_does_not_modify_snapshot_yaml():
    path = _project_root() / "alters" / "current" / "snapshot.yaml"
    h = _hash_file(path)
    client.get("/cycle-summary/current")
    client.get("/cycle-summary/validation")
    client.get("/cycle-summary/artifacts")
    assert _hash_file(path) == h


def test_api_does_not_modify_branches_yaml():
    path = _project_root() / "alters" / "current" / "branches.yaml"
    h = _hash_file(path)
    client.get("/cycle-summary/current")
    assert _hash_file(path) == h


def test_api_does_not_modify_reality_trace_yaml():
    path = _project_root() / "alters" / "current" / "reality_trace.yaml"
    h = _hash_file(path)
    client.get("/cycle-summary/current")
    assert _hash_file(path) == h


# --- API does not create score_*.yaml ---


def test_api_does_not_create_score_files():
    cal_dir = _project_root() / "alters" / "calibration" / "scores"
    before = set(cal_dir.glob("score_*.yaml")) if cal_dir.exists() else set()
    client.get("/cycle-summary/current")
    client.get("/cycle-summary/validation")
    client.get("/cycle-summary/artifacts")
    after = set(cal_dir.glob("score_*.yaml")) if cal_dir.exists() else set()
    assert after == before


# --- API does not create archive folders ---


def test_api_does_not_create_archive_folders():
    archive_dir = _project_root() / "alters" / "archive"
    before = set(archive_dir.glob("20*")) if archive_dir.exists() else set()
    client.get("/cycle-summary/current")
    client.get("/cycle-summary/validation")
    client.get("/cycle-summary/artifacts")
    after = set(archive_dir.glob("20*")) if archive_dir.exists() else set()
    assert after == before


# --- main.py does not include generation routers ---


def test_main_has_no_generation_routers():
    from alters_lab.main import app

    route_paths = [r.path for r in app.routes]
    forbidden_prefixes = ["/branch-discovery", "/alter-generation", "/dialogue", "/value-alignment", "/calibration", "/archive"]
    for prefix in forbidden_prefixes:
        for path in route_paths:
            if path.startswith("/calibration-loop") or path.startswith("/archive-mechanism") or path.startswith("/calibration-conversation"):
                continue
            assert not path.startswith(prefix), f"Found forbidden route: {path}"
