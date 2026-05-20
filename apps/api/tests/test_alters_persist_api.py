from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from alters_lab.main import app
from alters_lab.services.controlled_write import sha256_text

client = TestClient(app)


def _patch_alters_paths(monkeypatch, tmp_path):
    import alters_lab.api.alters as mod

    monkeypatch.setattr(mod, "get_alters_persist_base_dir", lambda: tmp_path / "alters")
    monkeypatch.setattr(mod, "get_alters_persist_audit_log_path", lambda: tmp_path / "audit.jsonl")
    monkeypatch.setattr(mod, "get_alters_persist_backup_dir", lambda: tmp_path / "backups")


def _valid_alter_request(alter_id: str = "alter_A", **overrides) -> dict:
    branch_ref = alter_id.replace("alter_", "branch_")
    req = {
        "approval_token": "test-token",
        "id": alter_id,
        "branch_ref": branch_ref,
        "label": f"Test {alter_id}",
        "source_refs": {
            "snapshot_ref": "alters/current/snapshot.yaml",
            "branches_ref": "alters/current/branches.yaml",
            "rubric_ref": "alters/calibration/rubric.yaml",
        },
        "quality_status": {"human_confirmed": True, "active": True},
        "voice": {"core_stance": "Test stance"},
    }
    req.update(overrides)
    return req


def _all_valid_alters_batch(**overrides) -> list[dict]:
    alters = []
    for aid in ("alter_A", "alter_B", "alter_C", "alter_D"):
        branch_ref = aid.replace("alter_", "branch_")
        alters.append({
            "id": aid,
            "branch_ref": branch_ref,
            "label": f"Test {aid}",
            "source_refs": {
                "snapshot_ref": "alters/current/snapshot.yaml",
                "branches_ref": "alters/current/branches.yaml",
                "rubric_ref": "alters/calibration/rubric.yaml",
            },
            "quality_status": {"human_confirmed": True, "active": True},
            "voice": {"core_stance": "Test stance"},
        })
    return alters


# --- health ---


def test_alters_health():
    r = client.get("/alters/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["component"] == "alters"
    assert body["mode"] == "controlled_write"


# --- single persist ---


def test_persist_accepts_arbitrary_token(monkeypatch, tmp_path):
    _patch_alters_paths(monkeypatch, tmp_path)
    r = client.post(
        "/alters/persist/alter_A",
        json=_valid_alter_request(approval_token="human-approval-token-123"),
    )
    assert r.status_code == 200
    assert r.json()["status"] == "persisted"


def test_persist_rejects_blank_token():
    r = client.post(
        "/alters/persist/alter_A",
        json=_valid_alter_request(approval_token=""),
    )
    assert r.status_code in (400, 422)


def test_persist_rejects_whitespace_token():
    r = client.post(
        "/alters/persist/alter_A",
        json=_valid_alter_request(approval_token="   "),
    )
    assert r.status_code in (400, 422)


def test_persist_rejects_id_mismatch():
    r = client.post(
        "/alters/persist/alter_B",
        json=_valid_alter_request(alter_id="alter_A"),
    )
    assert r.status_code == 400


def test_dry_run_returns_status_dry_run(monkeypatch, tmp_path):
    _patch_alters_paths(monkeypatch, tmp_path)
    r = client.post(
        "/alters/persist/alter_A",
        json=_valid_alter_request(dry_run=True),
    )
    assert r.status_code == 200
    assert r.json()["status"] == "dry_run"


def test_dry_run_does_not_write(monkeypatch, tmp_path):
    _patch_alters_paths(monkeypatch, tmp_path)
    client.post(
        "/alters/persist/alter_A",
        json=_valid_alter_request(dry_run=True),
    )
    assert not (tmp_path / "alters" / "alter_A.yaml").exists()


def test_dry_run_does_not_append_audit(monkeypatch, tmp_path):
    _patch_alters_paths(monkeypatch, tmp_path)
    client.post(
        "/alters/persist/alter_A",
        json=_valid_alter_request(dry_run=True),
    )
    assert not (tmp_path / "audit.jsonl").exists()


def test_dry_run_boundary_alters_not_modified(monkeypatch, tmp_path):
    _patch_alters_paths(monkeypatch, tmp_path)
    r = client.post(
        "/alters/persist/alter_A",
        json=_valid_alter_request(dry_run=True),
    )
    bc = r.json()["boundary_confirmations"]
    assert bc["alters_modified"] is False


def test_persist_writes_only_tmp_alter(monkeypatch, tmp_path):
    _patch_alters_paths(monkeypatch, tmp_path)
    r = client.post(
        "/alters/persist/alter_A",
        json=_valid_alter_request(),
    )
    assert r.status_code == 200
    assert (tmp_path / "alters" / "alter_A.yaml").exists()


def test_persist_response_includes_governance(monkeypatch, tmp_path):
    _patch_alters_paths(monkeypatch, tmp_path)
    r = client.post(
        "/alters/persist/alter_A",
        json=_valid_alter_request(),
    )
    body = r.json()
    assert "governance_check" in body
    assert body["governance_check"]["valid"] is True


def test_persist_response_boundary_confirmations(monkeypatch, tmp_path):
    _patch_alters_paths(monkeypatch, tmp_path)
    r = client.post(
        "/alters/persist/alter_A",
        json=_valid_alter_request(),
    )
    bc = r.json()["boundary_confirmations"]
    assert bc["alters_modified"] is True
    assert bc["snapshot_yaml_modified"] is False
    assert bc["branches_yaml_modified"] is False
    assert bc["value_alignment_modified"] is False
    assert bc["dialogue_modified"] is False
    assert bc["provider_used"] is False


def test_persist_response_no_raw_token(monkeypatch, tmp_path):
    _patch_alters_paths(monkeypatch, tmp_path)
    raw_token = "human-approval-token-123"
    r = client.post(
        "/alters/persist/alter_A",
        json=_valid_alter_request(approval_token=raw_token),
    )
    body_str = json.dumps(r.json())
    assert raw_token not in body_str


def test_audit_log_has_exact_hash(monkeypatch, tmp_path):
    _patch_alters_paths(monkeypatch, tmp_path)
    raw_token = "human-approval-token-123"
    client.post(
        "/alters/persist/alter_A",
        json=_valid_alter_request(approval_token=raw_token),
    )
    lines = (tmp_path / "audit.jsonl").read_text().strip().splitlines()
    record = json.loads(lines[0])
    assert record["approval_token_hash"] == sha256_text(raw_token)


# --- batch persist ---


def test_batch_persist_all_valid(monkeypatch, tmp_path):
    _patch_alters_paths(monkeypatch, tmp_path)
    r = client.post(
        "/alters/persist-batch",
        json={"approval_token": "test-token", "alters": _all_valid_alters_batch()},
    )
    assert r.status_code == 200
    assert r.json()["status"] == "persisted"
    assert len(r.json()["written_paths"]) == 4


def test_batch_persist_rejects_if_any_invalid(monkeypatch, tmp_path):
    _patch_alters_paths(monkeypatch, tmp_path)
    alters = _all_valid_alters_batch()
    alters[0]["id"] = "alter_X"
    r = client.post(
        "/alters/persist-batch",
        json={"approval_token": "test-token", "alters": alters},
    )
    assert r.status_code in (403, 422)


def test_batch_dry_run_does_not_write(monkeypatch, tmp_path):
    _patch_alters_paths(monkeypatch, tmp_path)
    r = client.post(
        "/alters/persist-batch",
        json={"approval_token": "test-token", "dry_run": True, "alters": _all_valid_alters_batch()},
    )
    assert r.json()["status"] == "dry_run"
    assert not (tmp_path / "alters").exists()


def test_batch_response_no_raw_token(monkeypatch, tmp_path):
    _patch_alters_paths(monkeypatch, tmp_path)
    raw_token = "human-approval-token-123"
    r = client.post(
        "/alters/persist-batch",
        json={"approval_token": raw_token, "alters": _all_valid_alters_batch()},
    )
    body_str = json.dumps(r.json())
    assert raw_token not in body_str


# --- forbidden field smuggling ---


def test_rejects_top_level_provider():
    r = client.post(
        "/alters/persist/alter_A",
        json=_valid_alter_request(provider={"name": "openai"}),
    )
    assert r.status_code == 422


def test_rejects_top_level_dialogue():
    r = client.post(
        "/alters/persist/alter_A",
        json=_valid_alter_request(dialogue={"session": "test"}),
    )
    assert r.status_code == 422


def test_rejects_top_level_archive():
    r = client.post(
        "/alters/persist/alter_A",
        json=_valid_alter_request(archive={"cycle": "2026-01"}),
    )
    assert r.status_code == 422


def test_rejects_top_level_database():
    r = client.post(
        "/alters/persist/alter_A",
        json=_valid_alter_request(database={"engine": "postgres"}),
    )
    assert r.status_code == 422


def test_rejects_top_level_frontend():
    r = client.post(
        "/alters/persist/alter_A",
        json=_valid_alter_request(frontend={"framework": "react"}),
    )
    assert r.status_code == 422


def test_rejects_top_level_generation():
    r = client.post(
        "/alters/persist/alter_A",
        json=_valid_alter_request(generation={"model": "gpt-4"}),
    )
    assert r.status_code == 422


def test_rejects_top_level_calibration_scoring():
    r = client.post(
        "/alters/persist/alter_A",
        json=_valid_alter_request(calibration_scoring={"score": 0.9}),
    )
    assert r.status_code == 422


def test_rejects_top_level_drift():
    r = client.post(
        "/alters/persist/alter_A",
        json=_valid_alter_request(drift={"value": 0.1}),
    )
    assert r.status_code == 422


def test_rejects_nested_voice_extra_field():
    req = _valid_alter_request()
    req["voice"]["dialogue"] = True
    r = client.post("/alters/persist/alter_A", json=req)
    assert r.status_code == 422


def test_rejects_batch_request_with_extra_field():
    r = client.post(
        "/alters/persist-batch",
        json={"approval_token": "test-token", "alters": [], "archive": True},
    )
    assert r.status_code == 422


# --- no generation runtime ---


def test_no_generation_runtime_routers():
    from alters_lab.main import app as _app

    routes = [route.path for route in _app.routes]
    for forbidden in ["branch-discovery", "alter-generation", "dialogue", "calibration", "archive"]:
        for route in routes:
            if forbidden in route.lower() and route != "/health" and not route.startswith("/alter-dialogue") and not route.startswith("/calibration-loop") and not route.startswith("/archive-mechanism") and not route.startswith("/provider-dialogue"):
                pytest.fail(f"Unexpected route containing '{forbidden}': {route}")
