from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from alters_lab.main import app
from alters_lab.services.controlled_write import sha256_text

client = TestClient(app)


def _patch_branches_paths(monkeypatch, tmp_path):
    import alters_lab.api.branches as mod

    monkeypatch.setattr(mod, "get_branches_persist_target_path", lambda: tmp_path / "branches.yaml")
    monkeypatch.setattr(mod, "get_branches_persist_audit_log_path", lambda: tmp_path / "audit.jsonl")
    monkeypatch.setattr(mod, "get_branches_persist_backup_dir", lambda: tmp_path / "backups")


def _valid_branches_request(**overrides) -> dict:
    req = {
        "approval_token": "test-token",
        "branch_discovery": {
            "status": "completed",
            "source_snapshot_ref": "alters/current/snapshot.yaml",
            "confirmed_by": "human_owner",
            "confirmation_note": "Test.",
        },
        "branches": [
            {"id": "branch_A", "label": "A", "core_choice": "c", "structural_commitment": "s", "key_tension_resolved": "t", "incompatible_with": ["branch_B", "branch_C", "branch_D"]},
            {"id": "branch_B", "label": "B", "core_choice": "c", "structural_commitment": "s", "key_tension_resolved": "t", "incompatible_with": ["branch_A", "branch_C", "branch_D"]},
            {"id": "branch_C", "label": "C", "core_choice": "c", "structural_commitment": "s", "key_tension_resolved": "t", "incompatible_with": ["branch_A", "branch_B", "branch_D"]},
            {"id": "branch_D", "label": "D", "core_choice": "c", "structural_commitment": "s", "key_tension_resolved": "t", "incompatible_with": ["branch_A", "branch_B", "branch_C"]},
        ],
    }
    req.update(overrides)
    return req


# --- health ---


def test_branches_health():
    r = client.get("/branches/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["component"] == "branches"
    assert body["mode"] == "controlled_write"


# --- persist accepts arbitrary token ---


def test_persist_accepts_arbitrary_token(monkeypatch, tmp_path):
    _patch_branches_paths(monkeypatch, tmp_path)
    r = client.post(
        "/branches/persist",
        json=_valid_branches_request(approval_token="human-approval-token-123"),
    )
    assert r.status_code == 200
    assert r.json()["status"] == "persisted"


# --- reject blank/whitespace token ---


def test_persist_rejects_blank_token():
    r = client.post(
        "/branches/persist",
        json=_valid_branches_request(approval_token=""),
    )
    assert r.status_code in (400, 422)


def test_persist_rejects_whitespace_token():
    r = client.post(
        "/branches/persist",
        json=_valid_branches_request(approval_token="   "),
    )
    assert r.status_code in (400, 422)


# --- dry_run ---


def test_dry_run_returns_status_dry_run(monkeypatch, tmp_path):
    _patch_branches_paths(monkeypatch, tmp_path)
    r = client.post(
        "/branches/persist",
        json=_valid_branches_request(dry_run=True),
    )
    assert r.status_code == 200
    assert r.json()["status"] == "dry_run"


def test_dry_run_does_not_write_target(monkeypatch, tmp_path):
    _patch_branches_paths(monkeypatch, tmp_path)
    client.post(
        "/branches/persist",
        json=_valid_branches_request(dry_run=True),
    )
    assert not (tmp_path / "branches.yaml").exists()


def test_dry_run_does_not_append_audit(monkeypatch, tmp_path):
    _patch_branches_paths(monkeypatch, tmp_path)
    client.post(
        "/branches/persist",
        json=_valid_branches_request(dry_run=True),
    )
    assert not (tmp_path / "audit.jsonl").exists()


def test_dry_run_response_no_full_yaml(monkeypatch, tmp_path):
    _patch_branches_paths(monkeypatch, tmp_path)
    r = client.post(
        "/branches/persist",
        json=_valid_branches_request(dry_run=True),
    )
    body = r.json()
    assert "would_write" not in body
    for key in body:
        val = body[key]
        if isinstance(val, str) and "branch_discovery:" in val:
            pytest.fail(f"Response field '{key}' contains full YAML content")


def test_dry_run_boundary_branches_not_modified(monkeypatch, tmp_path):
    _patch_branches_paths(monkeypatch, tmp_path)
    r = client.post(
        "/branches/persist",
        json=_valid_branches_request(dry_run=True),
    )
    bc = r.json()["boundary_confirmations"]
    assert bc["branches_yaml_modified"] is False


# --- persist writes only tmp branches.yaml ---


def test_persist_writes_only_tmp_branches(monkeypatch, tmp_path):
    _patch_branches_paths(monkeypatch, tmp_path)
    r = client.post(
        "/branches/persist",
        json=_valid_branches_request(),
    )
    assert r.status_code == 200
    assert (tmp_path / "branches.yaml").exists()


# --- persist response includes governance and boundary ---


def test_persist_response_includes_governance(monkeypatch, tmp_path):
    _patch_branches_paths(monkeypatch, tmp_path)
    r = client.post(
        "/branches/persist",
        json=_valid_branches_request(),
    )
    body = r.json()
    assert "governance_check" in body
    assert body["governance_check"]["valid"] is True


def test_persist_response_boundary_confirmations(monkeypatch, tmp_path):
    _patch_branches_paths(monkeypatch, tmp_path)
    r = client.post(
        "/branches/persist",
        json=_valid_branches_request(),
    )
    bc = r.json()["boundary_confirmations"]
    assert bc["branches_yaml_modified"] is True
    assert bc["snapshot_yaml_modified"] is False
    assert bc["alters_modified"] is False
    assert bc["value_alignment_modified"] is False
    assert bc["dialogue_modified"] is False
    assert bc["reality_trace_modified"] is False
    assert bc["calibration_score_created"] is False
    assert bc["drift_computed"] is False
    assert bc["archive_created"] is False
    assert bc["provider_used"] is False
    assert bc["frontend_added"] is False
    assert bc["database_added"] is False
    assert bc["generation_runtime_used"] is False


# --- no raw token in response ---


def test_persist_response_no_raw_token(monkeypatch, tmp_path):
    _patch_branches_paths(monkeypatch, tmp_path)
    raw_token = "human-approval-token-123"
    r = client.post(
        "/branches/persist",
        json=_valid_branches_request(approval_token=raw_token),
    )
    body_str = json.dumps(r.json())
    assert raw_token not in body_str


# --- audit log has exact hash ---


def test_audit_log_has_exact_hash(monkeypatch, tmp_path):
    _patch_branches_paths(monkeypatch, tmp_path)
    raw_token = "human-approval-token-123"
    client.post(
        "/branches/persist",
        json=_valid_branches_request(approval_token=raw_token),
    )
    lines = (tmp_path / "audit.jsonl").read_text().strip().splitlines()
    record = json.loads(lines[0])
    assert record["approval_token_hash"] == sha256_text(raw_token)


# --- audit log no raw token ---


def test_audit_log_no_raw_token(monkeypatch, tmp_path):
    _patch_branches_paths(monkeypatch, tmp_path)
    raw_token = "human-approval-token-123"
    client.post(
        "/branches/persist",
        json=_valid_branches_request(approval_token=raw_token),
    )
    content = (tmp_path / "audit.jsonl").read_text()
    assert raw_token not in content


# --- governance rejects incomplete payload ---


def test_governance_rejects_incomplete_status():
    r = client.post(
        "/branches/persist",
        json=_valid_branches_request(
            branch_discovery={"status": "not_started", "source_snapshot_ref": "", "confirmed_by": "", "confirmation_note": ""},
        ),
    )
    assert r.status_code == 403


# --- forbidden field smuggling ---


def test_rejects_top_level_calibration():
    r = client.post(
        "/branches/persist",
        json=_valid_branches_request(calibration={"score": 0.9}),
    )
    assert r.status_code == 422


def test_rejects_top_level_archive():
    r = client.post(
        "/branches/persist",
        json=_valid_branches_request(archive={"cycle": "2026-01"}),
    )
    assert r.status_code == 422


def test_rejects_top_level_provider():
    r = client.post(
        "/branches/persist",
        json=_valid_branches_request(provider={"name": "openai"}),
    )
    assert r.status_code == 422


def test_rejects_top_level_dialogue():
    r = client.post(
        "/branches/persist",
        json=_valid_branches_request(dialogue={"session": "test"}),
    )
    assert r.status_code == 422


def test_rejects_top_level_runtime():
    r = client.post(
        "/branches/persist",
        json=_valid_branches_request(runtime=True),
    )
    assert r.status_code == 422


def test_rejects_request_level_extra_field():
    req = _valid_branches_request()
    req["runtime"] = True
    r = client.post("/branches/persist", json=req)
    assert r.status_code == 422


def test_rejects_nested_branch_item_extra_field():
    req = _valid_branches_request()
    req["branches"][0]["alter_generation"] = True
    r = client.post("/branches/persist", json=req)
    assert r.status_code == 422


# --- no generation runtime ---


def test_no_generation_runtime_routers():
    from alters_lab.main import app as _app

    routes = [route.path for route in _app.routes]
    for forbidden in ["branch-discovery", "alter-generation", "dialogue", "calibration", "archive"]:
        for route in routes:
            if forbidden in route.lower() and route != "/health" and not route.startswith("/alter-dialogue") and not route.startswith("/calibration-loop") and not route.startswith("/archive-mechanism") and not route.startswith("/provider-dialogue"):
                pytest.fail(f"Unexpected route containing '{forbidden}': {route}")
